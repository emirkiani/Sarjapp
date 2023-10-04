from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('stations', FirmRecordView.as_view()),
    path('recommendation', RecommendationView.as_view()),
    path('station_detail/<int:station_id>', StationDetails.as_view()),
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
    path('favoritestations',FavoriteStationView.as_view()),
    path('routestations',RouteStationView.as_view()),
    path('profile',UserProfile.as_view()),
    path('user_criteria', CriteriaView.as_view()),
    path('user_criteria/<int:id>', CriteriaView.as_view()),
    path('station_search', StationSearchView.as_view()),
]
