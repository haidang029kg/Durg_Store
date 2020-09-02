from bulk_sync import bulk_sync
from django.db.models import Q
from rest_framework import serializers

from apps.drug.models import Drug, Category, Pharmacy, Prescription, PrescriptionDetail
from apps.drug.signals import signal_update_or_create_prescription


# Serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        read_only_fields = ['created', 'updated']
        exclude = ['is_removed']


class DrugSerializers(serializers.ModelSerializer):
    class Meta:
        model = Drug
        read_only_fields = ['created', 'updated', 'id']
        exclude = ['is_removed']

    def to_representation(self, instance):
        self.fields['category'] = CategorySerializer(read_only=True)
        return super(DrugSerializers, self).to_representation(instance)


class DrugCategorySerializer(serializers.ModelSerializer):
    ratio = serializers.SerializerMethodField()

    class Meta:
        model = Category
        read_only_fields = ['created', 'updated', 'id', 'ratio']
        exclude = ['is_removed']

    def get_ratio(self, obj):
        category = Drug.objects.filter(category__id=obj.id).count()
        other = Drug.objects.filter(~Q(category__id=obj.id)).count()
        return {
            'category': category,
            'other': other
        }


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        read_only_fields = ['id']
        exclude = ['is_removed']


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionDetail
        read_only_fields = ['id', 'prescription']
        exclude = ['is_removed', 'created', 'modified']

    def to_representation(self, instance):
        self.fields['drug'] = DrugSerializers(read_only=True)
        return super(PrescriptionDetailSerializer, self).to_representation(instance)


class PrescriptionSerializer(serializers.ModelSerializer):
    list_prescription_detail = PrescriptionDetailSerializer(many=True, write_only=True)

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

        res = super(PrescriptionSerializer, self).update(instance, validated_data)
        signal_update_or_create_prescription.send(self.__class__, prescription_id=instance.id)
        return res

    @classmethod
    def _bulk_sync(cls, filters, new_models: [PrescriptionDetail]):
        bulk_sync(
            new_models=new_models,
            filters=filters,
            fields=['drug', 'quantity', 'price_at_the_time', 'is_removed', 'is_available'],
            key_fields=['drug'])

    def to_representation(self, instance):
        self.fields['pharmacy'] = PharmacySerializer(read_only=True)
        return super(PrescriptionSerializer, self).to_representation(instance)
