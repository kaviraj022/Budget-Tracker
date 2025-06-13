from django.shortcuts import render, redirect
from django.contrib import messages
import mysql.connector
from django.conf import settings

# Create your views here.

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="your_username",
                password="your_password",
                database="budget_tracker"
            )
            cursor = conn.cursor(dictionary=True)
            
            # Check if user exists and password matches
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            
            if user:
                # Store user info in session
                request.session['user_id'] = user['id']
                request.session['username'] = user['username']
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
                
        except mysql.connector.Error as err:
            messages.error(request, f'Database error: {err}')
            
        finally:
            if 'conn' in locals():
                conn.close()
                
    return render(request, 'core/signin.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Connect to MySQL database
            conn = mysql.connector.connect(
                host="localhost",
                user="your_username",
                password="your_password",
                database="budget_tracker"
            )
            cursor = conn.cursor(dictionary=True)
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                messages.error(request, 'Username or email already exists.')
            else:
                # Insert new user
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password)
                )
                conn.commit()
                messages.success(request, 'Account created successfully! Please sign in.')
                return redirect('signin')
                
        except mysql.connector.Error as err:
            messages.error(request, f'Database error: {err}')
            
        finally:
            if 'conn' in locals():
                conn.close()
                
    return render(request, 'core/signup.html')
