from django.db.models import Q
from rest_framework import serializers
from bulk_sync import bulk_sync
from apps.drug.models import Drug, Category, Pharmacy, Prescription, PrescriptionDetail


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
    class Meta:
        model = Category
        read_only_fields = ['created', 'updated', 'id']
        exclude = ['is_removed']


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        read_only_fields = ['id']
        exclude = ['is_removed', 'created', 'modified']


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
            list_prescription_detail_models.append(PrescriptionDetail(prescription=prescription, **item))

        filters = Q(prescription=prescription)
        bulk_sync(
            new_models=list_prescription_detail_models,
            filters=filters,
            fields=['drug', 'quantity', 'price_at_the_time'],
            key_fields=['drug'])

        return prescription

    def update(self, instance, validated_data):
        list_prescription_detail_data = validated_data.get('list_prescription_detail', None)
        if list_prescription_detail_data:
            list_prescription_detail_data = validated_data.pop('list_prescription_detail')
            list_prescription_detail_models = []
            for item in list_prescription_detail_data:
                list_prescription_detail_models.append(PrescriptionDetail(prescription=instance, **item))

            filters = Q(prescription=instance)
            bulk_sync(
                new_models=list_prescription_detail_models,
                filters=filters,
                fields=['drug', 'quantity', 'price_at_the_time'],
                key_fields=['drug'])
        return super(PrescriptionSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        self.fields['pharmacy'] = PharmacySerializer(read_only=True)
        return super(PrescriptionSerializer, self).to_representation(instance)
