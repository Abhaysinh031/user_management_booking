from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import login , logout
from .forms import RegisterForm
from .models import Movie, Showtime, Seat, Reservation
from django.contrib.auth.views import LoginView
import stripe
from django.conf import settings
from accounts.models import Movie
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Showtime, Seat
from .forms import SeatBookingForm

# stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, 'accounts/home.html')

def index(request):
    return render(request, 'accounts/index.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    

def custom_logout_view(request):
    logout(request)
    return redirect('/home')    

#  movie selection 
@login_required
def movie_list(request):
    movies = Movie.objects.all()
    return render(request, 'accounts/movie_list.html', {'movies': movies})

# Showtime and Seat Selection 
@login_required
def showtime_detail(request, showtime_id, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    # Retrieve the Showtime associated with the Movie or return 404 if not found
    showtime = get_object_or_404(Showtime, id=showtime_id, movie_id=movie_id)
    showtime = Showtime.objects.get(id=showtime_id)
    seats = Seat.objects.filter(showtime=showtime)
    return render(request, 'accounts/showtime_detail.html', {'showtime': showtime, 'seats': seats , 'movie': movie})

@login_required
def book_seats(request, showtime_id):
    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        showtime = Showtime.objects.get(id=showtime_id)
        seats = Seat.objects.filter(showtime=showtime, id__in=selected_seats)
        total_price = len(seats) * 10.0  # Assume each seat costs $10
        reservation = Reservation.objects.create(user=request.user, showtime=showtime, total_price=total_price)
        reservation.seats.set(seats)
        for seat in seats:
            seat.is_booked = True
            seat.save()
        return redirect('payment', reservation_id=reservation.id)
    else:
        return redirect('showtime_detail', showtime_id=showtime_id)



@login_required
def seat_booking(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    seats = Seat.objects.filter(showtime=showtime)
    ticket_price = showtime.ticket_price
    if request.method == 'POST':
        selected_seat_id = request.POST.get('seat_id')
        if selected_seat_id:
            try:
                selected_seat = Seat.objects.get(id=selected_seat_id, showtime=showtime)
                # Redirect to the booking confirmation page
                return redirect('payment', showtime_id=showtime.id, seat_id=selected_seat.id)
            except Seat.DoesNotExist:
                # Handle the case where the seat does not exist
                return render(request, 'accounts/seat_booking.html', {
                    'showtime': showtime,
                    'seats': seats,
                    'ticket_price': ticket_price,
                    'error_message': 'The selected seat does not exist.'
                })
    
    return render(request, 'accounts/seat_booking.html', {'showtime': showtime, 'seats': seats, 'ticket_price':ticket_price})


@login_required
def payment(request, showtime_id, seat_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    seat = get_object_or_404(Seat, id=seat_id, showtime=showtime)

    paypalrestsdk.configure({
        "mode": settings.PAYPAL_MODE,
        "client_id": settings.PAYPAL_CLIENT_ID,
        "client_secret": settings.PAYPAL_CLIENT_SECRET
    })

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payment_execute', args=[showtime.id, seat.id])),
            "cancel_url": request.build_absolute_uri(reverse('payment_cancelled', args=[showtime.id, seat.id]))
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"Ticket for {showtime.movie.title}",
                    "sku": "001",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "10.00",
                "currency": "USD"
            },
            "description": f"Ticket for {showtime.movie.title}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                return redirect(approval_url)
    else:
        return render(request, 'accounts/payment_failure.html', {'error': payment.error})
    

@login_required
def payment_execute(request, showtime_id, seat_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    seat = get_object_or_404(Seat, id=seat_id, showtime=showtime)
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        if not seat.is_booked:
            seat.is_booked = True
            seat.user = request.user
            seat.save()
            return render(request, 'accounts/booking_success.html', {'seat': seat, 'showtime': showtime})
    else:
        print(payment.error)

    return render(request, 'accounts/booking_failure.html', {'seat': seat, 'showtime': showtime})

@login_required
def payment_cancelled(request, showtime_id, seat_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    seat = get_object_or_404(Seat, id=seat_id, showtime=showtime)
    return render(request, 'accounts/payment_cancelled.html', {'seat': seat, 'showtime': showtime})

@login_required
def booking_confirmation(request, showtime_id, seat_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    seat = get_object_or_404(Seat, id=seat_id, showtime=showtime)
    
    if request.method == 'POST':
        if not seat.is_booked:
            seat.is_booked = True
            seat.user = request.user  # Set the user who booked the seat
            seat.save()
            return render(request, 'accounts/booking_success.html', {'seat': seat, 'showtime': showtime})
        else:
            return render(request, 'accounts/booking_failure.html', {'seat': seat, 'showtime': showtime})
    
    return render(request, 'accounts/booking_confirmation.html', {'showtime': showtime, 'seat': seat})
import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Showtime, Seat

paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,  # sandbox or live
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})



# confirmation section
@login_required
def confirmation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    return render(request, 'accounts/confirmation.html', {'reservation': reservation})
