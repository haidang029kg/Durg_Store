import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel

# Create your models here.
from apps.drug.config_static_variable import STATUS


class Category(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.TextField()

    def __str__(self):
        name = self.name if self.name else ''
        return name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Drug(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='drug', null=True)
    rate = models.FloatField(default=0, validators=[
        MaxValueValidator(10),
        MinValueValidator(0)
    ])
    price = models.FloatField(default=0, validators=[
        MinValueValidator(0)
    ])

    def __str__(self):
        name = self.name if self.name else ''
        return name


class Pharmacy(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=12)

    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'

    def __str__(self):
        name = self.name if self.name else ''
        return name


class Prescription(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    # staff_create = models.ForeignKey(null=True)
    # staff_last_modify = models.ForeignKey(null=True)
    status = models.CharField(max_length=11, choices=STATUS, default=STATUS[0][0])
    note = models.TextField(null=True)
    name = models.CharField(max_length=20, null=True, default=None)


class PrescriptionDetail(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    drug = models.ForeignKey(Drug, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(validators=[
        MinValueValidator(1)
    ])
    price_at_the_time = models.FloatField(default=0, validators=[
        MinValueValidator(0)
    ])
