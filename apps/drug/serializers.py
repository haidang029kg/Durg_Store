from django.db.models import Q
from rest_framework import serializers

from apps.drug.models import Drug, Category, Pharmacy, Prescription, PrescriptionDetail, WorkSpace
from apps.drug.services.custom_bulk_sync import custom_bulk_sync
from apps.drug.signals import signal_update_or_create_prescription


# Serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        read_only_fields = ['created', 'updated']
        exclude = ['is_removed']


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        read_only_fields = ['created', 'updated', 'id']
        exclude = ['is_removed']


class DrugDetailSerializer(DrugSerializer):
    category = CategorySerializer()


class DrugCategorySerializer(serializers.ModelSerializer):
    ratio = serializers.SerializerMethodField()

    class Meta:
        model = Category
        read_only_fields = ['created', 'updated', 'id', 'ratio']
        exclude = ['is_removed']

    @classmethod
    def get_ratio(cls, obj):
        category = Drug.objects.filter(category__id=obj.id).count()
        other = Drug.objects.filter(~Q(category__id=obj.id)).count()
        return {
            'category': category,
            'other': other
        }


class WorkSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSpace
        exclude = ['is_removed', 'owner']


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        read_only_fields = ['id']
        exclude = ['is_removed']

    def create(self, validated_data):
        work_space = self.context.get('work_space')
        validated_data.update({"work_space": work_space})
        return super(PharmacySerializer, self).create(validated_data)


class PharmacyDetailSerializer(PharmacySerializer):
    work_space = WorkSpaceSerializer(read_only=True)


class PrescriptionDrugContentDetailSerializer(serializers.ModelSerializer):
    drug = DrugDetailSerializer()

    class Meta:
        model = PrescriptionDetail
        read_only_fields = ['id', 'prescription']
        exclude = ['is_removed', 'created', 'modified']


class PrescriptionDrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionDetail
        read_only_fields = ['id', 'prescription']
        exclude = ['is_removed', 'created', 'modified']


class PrescriptionDrugContentSerializer(serializers.ModelSerializer):
    list_prescription_detail = PrescriptionDrugSerializer(many=True, write_only=True)

    class Meta:
        model = Prescription
        read_only_fields = ['id']
        exclude = ['is_removed']

    def create(self, validated_data):
        list_prescription_detail_data = validated_data.pop('list_prescription_detail')
        prescription = Prescription.objects.create(**validated_data)
        list_prescription_detail_models = []
        for item in list_prescription_detail_data:
            list_prescription_detail_models.append(PrescriptionDetail(prescription=prescription, is_removed=False,
                                                                      **item))

        filters = Q(prescription=prescription)
        self._bulk_sync(filters, list_prescription_detail_models)
        signal_update_or_create_prescription.send(self.__class__, prescription_id=prescription.id)
        return prescription

    def update(self, instance, validated_data):
        list_prescription_detail_data = validated_data.get('list_prescription_detail', None)
        if list_prescription_detail_data:
            list_prescription_detail_data = validated_data.pop('list_prescription_detail')
            list_prescription_detail_models = []
            for item in list_prescription_detail_data:
                list_prescription_detail_models.append(PrescriptionDetail(prescription=instance, is_removed=False,
                                                                          **item))
            filters = Q(prescription=instance)
            self._bulk_sync(filters, list_prescription_detail_models)

        res = super(PrescriptionDrugContentSerializer, self).update(instance, validated_data)
        signal_update_or_create_prescription.send(self.__class__, prescription_id=instance.id)
        return res

    @classmethod
    def _bulk_sync(cls, filters, new_models: [PrescriptionDetail]):
        custom_bulk_sync(
            new_models=new_models,
            filters=filters,
            fields=['drug', 'prescription', 'quantity', 'price_at_the_time', 'is_removed'],
            key_fields=['drug', 'prescription'])


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer()
    work_space = WorkSpaceSerializer()

    class Meta:
        model = Prescription
        read_only_fields = ['id']
        exclude = ['is_removed']


class PrescriptionUpdateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        read_only_fields = ['id']
        exclude = ['is_removed', 'pharmacy', 'work_space']


class BulkCreateDrugSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    list_name = serializers.ListField(child=serializers.CharField())

    def validate(self, attrs):
        list_name = attrs.get("list_name")
        list_name = list(set(list_name))
        for name in list_name:
            if Drug.objects.filter(name=name).exists():
                raise serializers.ValidationError(f'{name} exists in the inventory')
        return list_name

    def bulk_create(self):
        first_category = Category.objects.all().order_by('created').first()
        bucket = []
        for name in self.validated_data:
            bucket.append(Drug(name=name, category=first_category, price=1))
        res = Drug.objects.bulk_create(bucket)
        return DrugSerializer(res, many=True).data


class SendMailPrescriptionSerializer(serializers.Serializer):
    prescription_id = serializers.UUIDField()

    @classmethod
    def validate_prescription_id(cls, value):
        try:
            Prescription.objects.get(pk=value)
            return value
        except Prescription.DoesNotExist:
            raise serializers.ValidationError('Prescription does not exist!')

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
