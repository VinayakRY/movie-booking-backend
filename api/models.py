from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.IntegerField()

    def __str__(self):
        return self.title


class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    total_seats = models.IntegerField()

    def __str__(self):
        return f"{self.movie.title} - {self.screen_name}"


class Booking(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('show', 'seat_number')
