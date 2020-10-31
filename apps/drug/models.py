import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel

from apps.drug.config import STATUS, IN_PROGRESS_KEY


# Create your models here.


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
    key = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        name = self.name if self.name else ''
        return name


class WorkSpace(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        name = self.name if self.name else ""
        return name


class UserWorkSpace(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    work_space = models.ForeignKey(WorkSpace, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'work_space')

    def __str__(self):
        user_name = self.user.username if self.user.username else ""
        ws_name = self.work_space.name if self.work_space.name else ""
        return f'{ws_name} --- {user_name}'


class Pharmacy(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    work_space = models.ForeignKey(WorkSpace, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    phone = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True, default=None)

    class Meta:
        verbose_name = 'Pharmacy'
        verbose_name_plural = 'Pharmacies'

    def __str__(self):
        name = self.name if self.name else ''
        return name


class Prescription(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    work_space = models.ForeignKey(WorkSpace, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=STATUS, default=IN_PROGRESS_KEY)
    note = models.TextField(null=True)
    name = models.CharField(max_length=20, null=True, default=None)

    total_price = models.FloatField(default=0, validators=[
        MinValueValidator(0)
    ])


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

    class Meta:
        unique_together = ('prescription', 'drug')
