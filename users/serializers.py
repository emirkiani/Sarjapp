from csv import field_size_limit
from pickletools import read_long1
from re import search
from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'email', 'password', 'is_guest']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    #password Hash RFC2898 eklemek gerekiyor.
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id','name','power','status','connection_code']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id','user_id','charge_id','payment_status','payment_time','price']

class FirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = ['name','email']

class FirmSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = ['id','email']

class StationPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station_Price
        fields = ['AC','DC']

#Station Serizalizer dÃ¼zenlenecek
#Subquery ve left join kontrol edilicek
#indexlemek konusuna bakÄ±lÄ±cak (index sayÄ±larÄ± optimum tutulup(fazla olmasÄ± insert yavaÅŸlar). precise noktalara atÄ±lmalÄ±)
class StationLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station_location
        fields = ['full_adress','city','country','latitude','longitude']

class StationCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station_location
        fields = ['latitude','longitude','station_id','name']

class StationDenemeSerializer(serializers.ModelSerializer):
    power = serializers.SerializerMethodField()
    connector_type = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()


    class Meta:
        model = Station_location
        fields = ['latitude', 'longitude', 'station_id', 'name', 'power', 'connector_type', 'min_price', 'max_price']
    def get_connector_type(self, obj):
        return obj.station.connector_type
    def get_min_price(self, obj):
        return obj.station.station_price.AC
    def get_power(self, obj):
        connection = obj.station.connection.first()
        if connection:
            return connection.power
        return None
    def get_max_price(self, obj):
        return obj.station.station_price.DC

class StationSerializer(serializers.ModelSerializer):
    station_location = StationCoordinatesSerializer()
    class Meta:
        model = Station
        fields = ['id','name','station_location']

class StationDetailSerializer(serializers.ModelSerializer):
    prices = StationPriceSerializer(source ='station_price')
    location = StationLocationSerializer(source='station_location')
    firm = FirmSerializer()
    connection = ConnectionSerializer(many=True)
    class Meta:
        model = Station
        fields = ['id','name','description', 'capacity', 'on_time', 'off_time','status','prices','connection','location','firm','longitude','latitude']
        

class RecommendationSerializer(serializers.ModelSerializer):
    ac = serializers.IntegerField(source='station.station_price.AC')
    dc = serializers.IntegerField(source='station.station_price.DC')
    longitude = serializers.CharField()
    latitude = serializers.CharField()
    social_facilities = serializers.CharField()
    name = serializers.CharField(source='station.name')
    connection_name = serializers.SerializerMethodField()
    power = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_connection_name(self, obj):
        connection = obj.station.connection.first()
        if connection:
            return connection.name
        return None

    def get_power(self, obj):
        connection = obj.station.connection.first()
        if connection:
            return connection.power
        return None

    def get_status(self, obj):
        connection = obj.station.connection.first()
        if connection:
            return connection.status
        return None

    class Meta:
        model = Station_location
        fields = ['id','ac', 'dc', 'longitude', 'latitude', 'name', 'connection_name', 'power', 'status','social_facilities']




class CarlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car_list
        fields = ['id','brand','model','total_range','connection_type','connection_value']

class CarSerializer(serializers.ModelSerializer):
    car = CarlistSerializer()
    class Meta:
        model = Car
        fields = ['id','car','name','user','license_plate','battery_health','model_year']

class UserCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id','car','name','user','license_plate','battery_health','model_year']


class UserCarputSerialize(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'name', 'license_plate','battery_health']



class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adress
        fields = ['id','user','name','full_adress','city','counties','description','latitude','longitude']

class AdressputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adress
        fields = ['id','name','full_adress','description']
#dÃ¼zenlenecek favoriteserializer
class FavoriteSerializer(serializers.ModelSerializer):
    station = StationSerializer()
    class Meta:
        model = Favorites
        fields = ['station']
#station FavoritepostSerializer dÃ¼zenlenecek
class FavoritepostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ['user','station']

#station ReservationSerializer dÃ¼zenlenecek
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id','reserved_at', 'reservation_start_time', 'reservation_end_time','reserv_date','station','user','connection','status']

class ReservationgetSerializer(serializers.ModelSerializer):
    #Station
    station = StationSerializer()
    class Meta:
        model = Reservation
        fields = ['id','reserved_at', 'reservation_start_time', 'reservation_end_time','reserv_date','station','user','connection','status']

class ReservationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'reservation_start_time','reservation_end_time','reserv_date']

class ChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = ['id','user','reservation','station','connection','start_time','end_time','price','status']

class ChargeputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charge
        fields = ['id', 'end_time','price']
        
class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = cities
        fields = ['cityid','cityname']
        
class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = counties
        fields = ['countyid','countyname']
        
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = areas
        fields=['areaid','areaname']
        
class NeighborhoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = neighborhoods
        fields = ['neighborhoodid','neighborhoodname']


class Userinfoserializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields=['user','charge','payment_status','payment_time','price']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields=['ordar_status','order_date','charge_id','payment','user']


class AdressgetSerializer(serializers.ModelSerializer):
    city = CitiesSerializer()
    counties = CountySerializer()
    class Meta:
        model = Adress
        fields = ['id','user','name','full_adress','city','counties','description','latitude','longitude']


class FavoriteStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station_location
        fields = '__all__'

class FirmsearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firm
        fields = '__all__'

class StationLocationsearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station_location
        fields = '__all__'

class StationsearchSerializer(serializers.ModelSerializer):
    firm = FirmsearchSerializer()
    station_location = StationLocationsearchSerializer()

    class Meta:
        model = Station
        fields = '__all__'


class CriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criteria
        fields = ['id', 'user', 'Charge_speed', 'Social_facilities', 'Price']