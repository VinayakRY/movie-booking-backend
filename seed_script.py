from api.models import Movie, Show
from django.utils import timezone
import datetime

m1 = Movie.objects.create(title="Interstellar", duration_minutes=169)
m2 = Movie.objects.create(title="Inception", duration_minutes=148)

now = timezone.now()

Show.objects.create(movie=m1, screen_name="Screen 1", date_time=now + datetime.timedelta(days=1), total_seats=50)
Show.objects.create(movie=m2, screen_name="Screen 2", date_time=now + datetime.timedelta(days=2), total_seats=40)

print("Seed successful!")
