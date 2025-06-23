from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User, BankAccount, Transaction
from django.utils import timezone

# Create your views here.

def signin_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                messages.error(request, 'Invalid username/email or password')
                return redirect('signin')

        if check_password(password, user.password):
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

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

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

def dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    accounts = BankAccount.objects.filter(user=user)
    transactions = Transaction.objects.filter(user=user).order_by('-date')[:10]
    return render(request, 'core/dashboard.html', {'accounts': accounts, 'user': user, 'transactions': transactions})

def add_account_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        account_name = request.POST.get('account_name')
        if account_name:
            BankAccount.objects.create(user=user, account_name=account_name)
            messages.success(request, 'Account added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Account name is required.')
    return render(request, 'core/add_account.html')

def delete_account_view(request, account_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    account = get_object_or_404(BankAccount, id=account_id, user=user)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully!')
        return redirect('dashboard')
    return render(request, 'core/delete_account.html', {'account': account})

def add_transaction_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    accounts = BankAccount.objects.filter(user=user)
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        account_id = request.POST.get('account')
        to_account_id = request.POST.get('to_account')
        account = get_object_or_404(BankAccount, id=account_id, user=user)
        to_account = None
        if transaction_type == 'TRANSFER' and to_account_id:
            to_account = get_object_or_404(BankAccount, id=to_account_id, user=user)
        transaction = Transaction.objects.create(
            user=user,
            account=account,
            to_account=to_account,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            date=timezone.now().date()
        )
        # Update balances
        if transaction_type == 'INCOME':
            account.balance += float(amount)
            account.save()
        elif transaction_type == 'EXPENSE':
            account.balance -= float(amount)
            account.save()
        elif transaction_type == 'TRANSFER' and to_account:
            account.balance -= float(amount)
            to_account.balance += float(amount)
            account.save()
            to_account.save()
        messages.success(request, 'Transaction added successfully!')
        return redirect('dashboard')
    return render(request, 'core/add_transaction.html', {'accounts': accounts})

def delete_transaction_view(request, transaction_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    transaction = get_object_or_404(Transaction, id=transaction_id, user=user)
    if request.method == 'POST':
        # Reverse the transaction effect on account balances
        if transaction.transaction_type == 'INCOME':
            transaction.account.balance -= float(transaction.amount)
            transaction.account.save()
        elif transaction.transaction_type == 'EXPENSE':
            transaction.account.balance += float(transaction.amount)
            transaction.account.save()
        elif transaction.transaction_type == 'TRANSFER' and transaction.to_account:
            transaction.account.balance += float(transaction.amount)
            transaction.to_account.balance -= float(transaction.amount)
            transaction.account.save()
            transaction.to_account.save()
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    return render(request, 'core/delete_transaction.html', {'transaction': transaction})
