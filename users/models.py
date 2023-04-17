from ast import Add
from tkinter import CASCADE
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import AbstractUser
from django import forms


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=10)
    country = models.CharField(max_length=255)
    is_guest = models.BooleanField(default=False)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []     


class Firm(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)

class Station(models.Model):
    name = models.CharField(max_length=255)
    firm = models.ForeignKey(Firm, related_name='stations', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    capacity = models.IntegerField()
    on_time = models.CharField(max_length=255)
    off_time = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    

class Station_Price(models.Model):
    station = models.OneToOneField(Station, on_delete=models.CASCADE)
    AC = models.IntegerField()
    DC = models.IntegerField()

class Station_location(models.Model):
    station = models.OneToOneField(Station, on_delete=models.CASCADE)
    full_adress = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

class Connection(models.Model):
    name = models.CharField(max_length=255)
    station = models.ForeignKey(Station,related_name='connection', on_delete=models.CASCADE)
    power = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    connection_code = models.CharField(max_length=255)

class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)

class Car_list(models.Model):
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    total_range = models.CharField(max_length=255)
    connection_type = models.CharField(max_length=255)
    connection_value = models.CharField(max_length=255)

class Car(models.Model):
    car = models.ForeignKey(Car_list, related_name='carss', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=255)
    battery_health = models.IntegerField()
    model_year = models.IntegerField()


class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    started_at = models.DateTimeField()
    range = models.IntegerField()

class Reservation(models.Model):
    user = models.ForeignKey(User ,on_delete=models.CASCADE)
    station = models.ForeignKey(Station , on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField()
    reservation_start_time = models.TimeField()
    reservation_end_time = models.TimeField()
    status = models.CharField(max_length=255)
    reserv_date = models.DateField()

class Charge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, null=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    price = models.IntegerField(null=True)
    status = models.CharField(max_length=255)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    charge = models.OneToOneField(Charge, on_delete=models.CASCADE)
    price = models.FloatField(blank=True, null=True)
    payment_status = models.CharField(max_length=15)
    payment_time = models.DateTimeField()



class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    charge = models.OneToOneField(Charge, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=15)
    order_date = models.DateTimeField()

class areas(models.Model):
    areaid = models.IntegerField(primary_key=True)
    countyid = models.IntegerField()
    areaname = models.CharField(max_length=100)
    
class cities(models.Model):
    cityid = models.IntegerField(primary_key=True)
    countryid = models.IntegerField()
    cityname = models.CharField(max_length=100)
    plateno = models.CharField(max_length=2)
    phonecode = models.CharField(max_length=7)
    
class counties(models.Model):
    countyid = models.IntegerField(primary_key=True)
    cityid = models.IntegerField()
    countyname = models.CharField(max_length=50)
    
class countries(models.Model):
    countryid = models.IntegerField(primary_key=True)
    binarycode = models.CharField(max_length=2)
    triplecode = models.CharField(max_length=3)
    countryname = models.CharField(max_length=100)
    phonecode = models.CharField(max_length=6)
    
class neighborhoods(models.Model):
    neighborhoodid = models.IntegerField(primary_key=True)
    areaid = models.IntegerField()
    neighborhoodname = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)


class Adress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    full_adress = models.CharField(max_length=255)
    city = models.ForeignKey(cities,on_delete=models.CASCADE)
    counties = models.ForeignKey(counties,on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
