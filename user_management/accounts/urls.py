from django.urls import path
from .views import register, CustomLoginView ,home ,index, movie_list, showtime_detail, book_seats, payment, confirmation ,custom_logout_view, seat_booking
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("home/", home, name="home"),
    path("index/",index , name="index"),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('movies/', movie_list, name='movie_list'),
    path('movies/<int:movie_id>/showtimes/<int:showtime_id>/', views.showtime_detail, name='showtime_detail'),
    path('showtimes/<int:showtime_id>/seat_booking/', views.seat_booking, name='seat_booking'),
    path('showtimes/<int:showtime_id>/confirmation/<int:seat_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('showtimes/<int:showtime_id>/payment/<int:seat_id>/', views.payment, name='payment'),
    path('showtimes/<int:showtime_id>/payment_execute/<int:seat_id>/', views.payment_execute, name='payment_execute'),
    path('showtimes/<int:showtime_id>/payment_cancelled/<int:seat_id>/', views.payment_cancelled, name='payment_cancelled'),
    path('book/<int:showtime_id>/', book_seats, name='book_seats'),
    path('confirmation/<int:reservation_id>/', confirmation, name='confirmation'),
]
