from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User

# Create your views here.

def signin_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        try:
            # Try to find user by username or email
            user = User.objects.get(username=username_or_email) or User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid username/email or password')
            return redirect('signin')

        if check_password(password, user.password):
            # Store user info in session
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            messages.success(request, 'Logged in successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username/email or password')
            return redirect('signin')

    return render(request, 'core/signin.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        # Create new user
        hashed_password = make_password(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        user.save()

        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('signin')

    return render(request, 'core/signup.html')
