from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('stations', FirmRecordView.as_view()),
    path('car_list', CarListView.as_view()),
    path('user_car', CarView.as_view()),
    path('user_car/<int:id>', CarView.as_view()),
    path('user_adress', AdressView.as_view()),
    path('user_adress/<int:id>', AdressView.as_view()),
    path('favorites/<int:id>', FavoriteView.as_view()),
    path('favorites', FavoriteView.as_view()),
    path('reservation', ReservationView.as_view()),
    path('reservation/<int:id>', ReservationView.as_view()),
    path('reservation_date', ReservationDateView.as_view()),
    path('charge',ChargeView.as_view()),
    path('charge/<int:id>',ChargeView.as_view()),
    path('cities',CityView.as_view()),
    path('payment',PaymentView.as_view()),
]
