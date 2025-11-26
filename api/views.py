from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import SignupSerializer, MovieSerializer, ShowSerializer, BookingSerializer
from .models import Movie, Show, Booking
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class ShowListByMovieView(generics.ListAPIView):
    serializer_class = ShowSerializer

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Show.objects.filter(movie_id=movie_id)


class BookSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, show_id):
        seat_number = request.data.get("seat_number")

        # Validate presence and type
        if seat_number is None:
            return Response({"error": "seat_number is required"}, status=400)
        try:
            seat_number = int(seat_number)
        except (ValueError, TypeError):
            return Response({"error": "seat_number must be an integer"}, status=400)

        show = get_object_or_404(Show, id=show_id)

        # Validate seat bounds
        if seat_number < 1 or seat_number > show.total_seats:
            return Response({"error": f"seat_number must be between 1 and {show.total_seats}"}, status=400)

        # Prevent overbooking (count only currently booked seats)
        booked_count = Booking.objects.filter(show=show, status='booked').count()
        if booked_count >= show.total_seats:
            return Response({"error": "Show is fully booked"}, status=400)

        # Attempt to create booking; unique_together on (show, seat_number) prevents double booking.
        try:
            booking = Booking.objects.create(
                user=request.user,
                show=show,
                seat_number=seat_number,
                status='booked'
            )
        except IntegrityError:
            return Response({"error": "Seat already booked"}, status=400)
        except Exception as exc:
            return Response({"error": f"Unexpected error: {str(exc)}"}, status=500)

        return Response(BookingSerializer(booking).data, status=201)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        """
        Cancel a booking. To immediately free up the seat we DELETE the booking row.
        This keeps the unique constraint simple (no conditional unique index required).
        """
        booking = get_object_or_404(Booking, id=booking_id)

        # Security: only owner can cancel
        if booking.user != request.user:
            return Response({"error": "You cannot cancel someone else's booking"}, status=403)

        # Delete booking so the seat becomes available immediately
        booking.delete()
        return Response({"message": "Booking cancelled"}, status=200)


class MyBookingsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        # List bookings owned by the logged-in user (only existing bookings; cancelled ones are deleted)
        return Booking.objects.filter(user=self.request.user)
