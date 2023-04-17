from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import *
from .models import *
import jwt, datetime
#import iyzipay
from rest_framework import status
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        is_guest = request.data.get('is_guest', False)
        if is_guest:
            data = {
                'email': 'guest@example.com',  # or any other email you want to use for guest users
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
            # Guest login
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


class FirmRecordView(APIView):
    
    def get(self, request):
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        for i in range (len(serializer.data)):
            count = 0
            for j in range (len(serializer.data[i]['connection'])):
                if serializer.data[i]['connection'][j]['status'] == 'available':
                    count = count +1
                serializer.data[i]['available_station_count']= count
        return Response(serializer.data)

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
