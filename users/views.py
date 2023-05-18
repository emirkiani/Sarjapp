from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from .models import *
import jwt, datetime
import math
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from polyline import decode
import requests
import time
from django.db import connection
#from polyline.codec import PolylineCodec
#import iyzipay
from rest_framework import status
class RegisterView(APIView):
    def post(self, request):
        #guest girişi için mail fieldinın düzenlenmesi
        is_guest = request.data.get('is_guest', False)
        if is_guest:
            data = {
                'email': 'guest@example.com',
                'is_guest': True
            }
        else:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

        instance = User.objects.create(**data)

        payload = {
            'id': instance.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response



class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        if email is None and password is None:
            user = User.objects.create(email='guest@example.com', is_guest=True)
        else:
            user = User.objects.filter(email=email).first()

            if user is None:
                raise AuthenticationFailed('User not found!')

            if not user.check_password(password):
                raise AuthenticationFailed('Incorrect password!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response



class UserView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

#Stations verisi latitude longitude request içinde alarak dönecek
#station infoları parça parça get alıcak şekilde düzenlenecek
#Station Search 
#Station filtre APIsi yazılıcak
#Station AC/DC,KW Power, Rating,7/24,taşıt service,bireysel istisyon(sonra)
class FirmRecordView(APIView):
    
    def get(self, request):
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)
    
class StationDetails(APIView):
    
    def get(self, request, station_id):
        station = Station.objects.filter(id=station_id).first()
        if station:
            serializer = StationDetailSerializer(station)
            count = 0
            for connection in serializer.data['connection']:
                if connection['status'] == 'available':
                    count += 1
            serializer.data['available_station_count'] = count
            return Response(serializer.data)
        else:
            return Response({"error": "Station not found."}, status=status.HTTP_404_NOT_FOUND)

    
#Araç ile alakalı Veri incelenelip
class CarListView(APIView):
    
    def get(self, request):
        cars = Car_list.objects.all()
        serializer = CarlistSerializer(cars, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CarView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        cars = Car.objects.filter(user_id=payload['id'])
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)

    def post(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        request.data['user'] = payload['id']
        serializer = UserCarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, id):
        try:
            car = Car.objects.get(pk=id)
        except Car.DoesNotExist:
            return response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserCarputSerialize(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            car = Car.objects.get(pk=id)
        except Car.DoesNotExist:
            return response(status=status.HTTP_404_NOT_FOUND)

        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class AdressView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        adresses = Adress.objects.filter(user_id=payload['id'])
        serializer = AdressgetSerializer(adresses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        request.data['user'] = payload['id']
        serializer = AdressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, id):
        try:
            adress = Adress.objects.get(pk=id)
        except Adress.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = AdressputSerializer(adress, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            adress = Adress.objects.get(pk=id)
        except Adress.DoesNotExist:
            return response(status=status.HTTP_404_NOT_FOUND)
        adress.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class FavoriteView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        favorites = Favorites.objects.filter(user_id=payload['id'])
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        if Favorites.objects.filter(station=request.data['station']):
            favorite = Favorites.objects.filter(station=request.data['station'])
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            request.data['user'] = payload['id']    
            serializer = FavoritepostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReservationDateView(APIView):
    def post(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        reservations = Reservation.objects.filter(station_id=request.data['station'],connection_id=request.data['connection'],reserv_date=request.data['date'])
        seriazlizer = ReservationDateSerializer(reservations, many=True)
        return Response(seriazlizer.data)

class ReservationView(APIView):
    def post(self, request):

        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        request.data['user'] = payload['id']

        request.data['reserved_at'] = datetime.datetime.now()

        request.data['status'] = 'active'

        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):

        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        reservations = Reservation.objects.filter(user_id=payload['id'])
        serializer = ReservationgetSerializer(reservations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        try:
            reservation = Reservation.objects.get(pk=id)
        except Reservation.DoesNotExist:
            return response(status=status.HTTP_404_NOT_FOUND)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
#Charge başlatılıyor ama connection statusu değişmiyor (düzenlenecek)II
#Charge başlatıldığında dönen infolar yeterli değil(firmalar ile görüşme sonrası düzenlenmeli)II
class ChargeView(APIView):

    def post(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        reservation = Reservation.objects.filter(user_id=payload['id'])
        reservationserializer = ReservationSerializer(reservation, many=True)
        if reservationserializer.data == []:
            connection = Connection.objects.filter(id=request.data['connection'])
            connectionserializer = ConnectionSerializer(connection, many=True)
            if connectionserializer.data[0]['status'] == 'available':
                if connectionserializer.data[0]['connection_code'] == request.data['connection_code']:
                    request.data['user'] = payload['id']
                    request.data['start_time'] = datetime.datetime.now()
                    request.data['start_time'] = request.data['start_time'] - datetime.timedelta(microseconds=request.data['start_time'].microsecond)
                    request.data['status'] = 'Charging'
                    del request.data['connection_code']
                    chargeserializer = ChargeSerializer(data=request.data)
                    if chargeserializer.is_valid():
                        chargeserializer.save()
                    return Response(chargeserializer.data, status=status.HTTP_201_CREATED)
        else:
            connection = Connection.objects.filter(id=request.data['connection'])
            connectionserializer = ConnectionSerializer(connection, many=True)
            for data in reservationserializer.data:
                if data['station'] == request.data['station']:
                    if data['connection'] == request.data['connection']:
                        if connectionserializer.data[0]['connection_code'] == request.data['connection_code']:
                            request.data['reservation'] = data['id']
                            request.data['user'] = payload['id']
                            request.data['start_time'] = datetime.datetime.now()
                            request.data['start_time'] = request.data['start_time'] - datetime.timedelta(microseconds=request.data['start_time'].microsecond)
                            request.data['status'] = 'Charging'
                            del request.data['connection_code']
                            chargeserializer = ChargeSerializer(data=request.data)
                            if chargeserializer.is_valid():
                                chargeserializer.save()
                            return Response(chargeserializer.data, status=status.HTTP_201_CREATED)
                        else:
                            content={'Connection codu hatalı':'kodu tekrar giriniz'}
                            return Response(content, status=status.HTTP_424_FAILED_DEPENDENCY)
                    else:
                        content = {'istasyondaki Yanlış Connectiona bağlanmaya çalışıyorsun':'doğru connectiondan şarj etmeyi dene'}
                        return Response(content, status=status.HTTP_424_FAILED_DEPENDENCY)
                else:
                    content = {'Başka bir istasyonda rezervasyonun mevcüt yanlış istasyonda':'doğru istasyonda değilsin'}
                    return Response(content, status=status.HTTP_424_FAILED_DEPENDENCY)

            
    def put(self, request, id):
        try:
            charge = Charge.objects.get(pk=id)
        except charge.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializers = ChargeSerializer(charge)
        date_format1 = '%Y-%m-%dT%H:%M:%S.%fZ'
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        c = datetime.datetime.strptime(serializers.data['start_time'], date_format) - datetime.datetime.strptime(request.data['end_time'], date_format1)
        minutes = c.total_seconds() / 60
        if request.data['name'] == 'AC':
            request.data['price']=-int(50 * minutes)
        else:
            request.data['price']=-int(30 * minutes)

        serializer = ChargeputSerializer(charge, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        charges = Charge.objects.filter(user_id=payload['id'],end_time__isnull=True)
        serializer = ChargeSerializer(charges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CityView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
       
        city = cities.objects.all()
        serializer = CitiesSerializer(city, many = True)
        return Response(serializer.data)
        

    def post(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        if "cityid" in request.data.keys():
            county = counties.objects.filter(cityid = request.data["cityid"])
            serializer = CountySerializer(county,many = True)
            return Response(serializer.data)
        elif "countyid" in request.data.keys():
            area = areas.objects.filter(countyid = request.data["countyid"])
            serializer = AreaSerializer(area,many = True)
            return Response(serializer.data)
        elif "areaid" in request.data.keys():
            neighborhood = neighborhoods.objects.filter(areaid = request.data["areaid"])
            serializer = NeighborhoodSerializer(neighborhood,many=True)
            return Response(serializer.data)

#payment düzenlenecek()II
class PaymentView(APIView):

    def get(self, request):
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        orders = Payment.objects.filter(user_id=payload['id'],payment_status='done')
        serializer = PaymentSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        content=request.data
        token = request.headers.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        
        exp_month= request.data["payment_card"]["expireMonth"]
        exp_year=request.data["payment_card"]["expireYear"]
        currentMonth = datetime.datetime.now().month
        currentYear = datetime.datetime.now().year
        
        def luhn_checksum(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = 0
            checksum += sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10

        def is_luhn_valid(card_number):
            return luhn_checksum(card_number) == 0
    
        card_validation = is_luhn_valid(content["payment_card"]["cardNumber"])
        print ('Correct:' + str(card_validation))
        
        if card_validation == True and int(exp_year) >= currentYear :
            if int(exp_month) >= currentMonth :
                
                user_info = User.objects.filter(id=payload['id'])
                userserializer = Userinfoserializer(user_info, many=True)
                customer_info = userserializer.data
                #print(customer_info[0]["name"])
                options = {
                'api_key': 'sandbox-hZOXBeXnABAOVTHwluXJj3YBsgcHv1BZ',
                'secret_key': 'sandbox-xcy5IQ5LI4LTcpV67yHqf2YaGovPgk6H',
                'base_url': 'sandbox-api.iyzipay.com'
                }
                payment_card = content["payment_card"]

                buyer = {
                    'id': customer_info[0]["id"],
                    'name': customer_info[0]["name"],
                    'surname': customer_info[0]["surname"],
                    'gsmNumber': "+90" + customer_info[0]["surname"],
                    'email': customer_info[0]["email"],
                    'identityNumber': '74300864791',
                    'lastLoginDate': '2013-04-21 15:12:09',
                    'registrationDate': '2013-04-21 15:12:09',
                    'registrationAddress': content["customer_address"]["address"],
                    'ip': content["ip"],
                    'city': content["customer_address"]["city"],
                    'country': 'Turkey',
                    'zipCode': content["customer_address"]["zipCode"]
                }

                address = {
                    'contactName': customer_info[0]["name"],
                    'city': content["customer_address"]["city"],
                    'country': 'Turkey',
                    'address': content["customer_address"]["address"],
                    'zipCode': content["customer_address"]["zipCode"]
                }

                basket_items = [content["basket_items"]]
                request1 = {
                    'locale': 'tr',
                    'conversationId': '123456789',
                    'price': content["basket_items"]["price"],
                    'paidPrice': content["basket_items"]["price"],
                    'currency': 'TRY',
                    'installment': '1',
                    'basketId': content["basket_items"]["id"],
                    'paymentChannel': 'WEB',
                    'paymentGroup': 'PRODUCT',
                    'paymentCard': payment_card,
                    'buyer': buyer,
                    'shippingAddress': address,
                    'billingAddress': address,
                    'basketItems': basket_items
                }

                #payment = iyzipay.Payment().create(request1, options)
                #response = payment.read().decode('UTF-8')
                if response[11:18] == 'success':
                    info={}
                    info['user'] = int(customer_info[0]["id"])
                    info['charge'] = int(content["basket_items"]["id"])
                    info['payment_status'] = "done"
                    info['payment_time'] = datetime.datetime.now()
                    info['price'] = content["basket_items"]["price"]
                    serializer = PaymentSerializer(data=info)
                    if serializer.is_valid():
                        serializer.save()
                        
                    else :
                        print("merto",info)
                    return Response("Ödeme Başarılı")
                else :
                    return Response("Bir Sorun Oluştu")
                
                return Response(payment.read().decode('UTF-8'))
        
        

        
        #serializer = AdressSerializer(data=request.data)
        return Response(request)



#Favori istasyon algoritması için rota üzerinde (bütün noktalar dönücek)algoritma bakılacak
class FavoriteStationView(APIView):
    
    def get(self, request):
        latitude = float(request.data['latitude'])
        longitude = float(request.data['longitude'])
        diameter = float(request.data['diameter'])

        lat_r = radians(latitude)
        lon_r = radians(longitude)

        stations = Station_location.objects.filter(
            station__isnull=False,
            latitude__range=(latitude - (diameter / 111), latitude + (diameter / 111)),
            longitude__range=(longitude - (diameter / (111 * cos(lat_r))), longitude + (diameter / (111 * cos(lat_r)))),
        )

        for station in stations:
            station_lat_r = radians(float(station.latitude))
            station_lon_r = radians(float(station.longitude))
            dlon = station_lon_r - lon_r
            dlat = station_lat_r - lat_r
            a = sin(dlat/2)**2 + cos(lat_r) * cos(station_lat_r) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = 6371 * c
            print(distance)
            #station.distance = distance

        #stations = sorted(stations, key=lambda s: s.distance)
        #print(stations)
        serializer = FavoriteStationSerializer(stations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    






class RouteStationView(APIView):

    def get(self, request):
        start_latitude = float(request.data.get('start_latitude'))
        start_longitude = float(request.data.get('start_longitude'))
        dest_latitude = float(request.data.get('dest_latitude'))
        dest_longitude = float(request.data.get('dest_longitude'))

        route_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_latitude},{start_longitude}&destination={dest_latitude},{dest_longitude}&mode=driving&key=AIzaSyAMBbQy9wILxwW_jOn-LharzXsxMtVi1Bw'
        response = requests.get(route_url)
        if response.status_code != 200:
            return Response({'error': 'Unable to calculate route'}, status=status.HTTP_400_BAD_REQUEST)

        route_data = response.json()
        polyline = route_data['routes'][0]['overview_polyline']['points']
        route_coords = decode(polyline)
        new_route_coords = route_coords[::1]
        segment_length =5
        segments = []
        for i in range(0, len(new_route_coords) - 1):
            segment_start = new_route_coords[i]
            segment_end = new_route_coords[i + 1]
            segment_distance = self.calculate_distance(segment_start[0], segment_start[1], segment_end[0], segment_end[1])
            segment_steps = math.ceil(segment_distance / segment_length)
            for j in range(segment_steps):
                t = float(j) / segment_steps
                segment_lat = segment_start[0] * (1 - t) + segment_end[0] * t
                segment_lng = segment_start[1] * (1 - t) + segment_end[1] * t
                segments.append((segment_lat, segment_lng))
        stations = []
        segment_width = 10
        stations_distances = {}
        for segment in segments:
            min_lat, max_lat, min_lng, max_lng = self.calculate_bounding_box(segment[0], segment[1], segment_width)
            segment_stations = Station_location.objects.filter(latitude__gte=min_lat, latitude__lte=max_lat, longitude__gte=min_lng, longitude__lte=max_lng)
            for station in segment_stations:
                station_distance = self.calculate_distance(station.latitude,station.longitude,segment[0],segment[1])
                stations_distances[station.id] = station_distance
                if station_distance < 1:
                    stations.append(station)
        #print(connection.queries[-1]['sql'])
        # serializer = StationDetailSerializer(stations)
        serializer = StationLocationSerializer(stations, many=True)

        for data in serializer.data:
            data['distance']=stations_distances[data['id']]
            data['puan']=1-data['distance']
        return Response(serializer.data)

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        earth_radius = 6371  # in km
        lat1_rad = radians(lat1)
        lng1_rad = radians(lng1)
        lat2_rad = radians(lat2)
        lng2_rad = radians(lng2)
        d_lat = lat2_rad - lat1_rad
        d_lng = lng2_rad - lng1_rad
        a = sin(d_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(d_lng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return earth_radius * c

    def calculate_bounding_box(self, lat, lng, width):
        earth_radius = 6371  # in km
        d_lat = width / earth_radius
        d_lng = width / (earth_radius * cos(radians(lat)))
        min_lat = lat - d_lat
        max_lat = lat + d_lat
        min_lng = lng - d_lng
        max_lng = lng + d_lng
        return min_lat, max_lat, min_lng, max_lng
    
class UserProfile(APIView):
    def get(self, request):
        token = request.headers.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        cars = Car.objects.filter(user_id=payload['id'])
        car_serializer = CarSerializer(cars, many=True)
        adresses = Adress.objects.filter(user_id=payload['id'])
        adress_serializer = AdressSerializer(adresses, many=True)
        
        
        response_data = {
            'cars': car_serializer.data,
            'user_adress': adress_serializer.data
        }
        if response_data['cars'] :
            print("Araç Bilgisi Var")
        else:
            print("Araç Bilgisi Yok")
        if response_data['user_adress']:
            print("Adres Bilgisi Var")
        else:
            print("Adres Bilgisi Yok")
            
        return Response(response_data)