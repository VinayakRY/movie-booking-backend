from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('movies/', MovieListView.as_view()),
    path('movies/<int:movie_id>/shows/', ShowListByMovieView.as_view()),
    path('shows/<int:show_id>/book/', BookSeatView.as_view()),
    path('bookings/<int:booking_id>/cancel/', CancelBookingView.as_view()),
    path('my-bookings/', MyBookingsView.as_view()),
]
