from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2 , default=0) 

    def __str__(self):
        return f"{self.movie.title} at {self.start_time}"

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    row = models.CharField(max_length=10)
    number = models.PositiveIntegerField()
    is_booked = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)

    # def __str__(self):
    #     return f"Row {self.row}, Seat {self.number} for {self.showtime}"
    def __str__(self):
        return f'Row {self.row} Seat {self.number} - {"Booked" if self.is_booked else "Available"}'

    

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Reservation by {self.user.username} for {self.showtime}"

