from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Movie, Showtime, Seat 
admin.site.register(Movie)
admin.site.register(Showtime )
admin.site.register(Seat)
