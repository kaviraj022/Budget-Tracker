from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Account, Transaction, AMOUNT_TYPE_CHOICES
from django.utils import timezone
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .utils import user_login_required
from datetime import date
from decimal import Decimal

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

@user_login_required
def dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    accounts = Account.objects.filter(user=user)
    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')[:10]
    return render(request, 'core/dashboard.html', {
        'accounts': accounts,
        'user': user,
        'transactions': transactions,
        'today': date.today().isoformat(),
    })

@user_login_required
def add_account_view(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        account_name = request.POST.get('account_name')
        if account_name:
            Account.objects.create(user=user, account_name=account_name)
            messages.success(request, 'Account added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Account name is required.')
    return render(request, 'core/add_account.html')

@user_login_required
def delete_account_view(request, account_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    account = get_object_or_404(Account, id=account_id, user=user)
    if request.method == 'POST':
        # Roll back all transactions where this account is involved
        for transaction in account.transactions.all():
            amount = Decimal(str(transaction.amount))
            if transaction.transaction_type == 'INCOME':
                account.balance -= amount
            elif transaction.transaction_type == 'EXPENSE':
                account.balance += amount
            elif transaction.transaction_type == 'TRANSFER' and transaction.to_account:
                account.balance += amount
                transaction.to_account.balance -= amount
                transaction.to_account.save()
            account.save()
        # As to_account in transfers
        for transaction in account.received_transactions.all():
            amount = Decimal(str(transaction.amount))
            if transaction.transaction_type == 'TRANSFER' and transaction.account:
                transaction.account.balance += amount
                account.balance -= amount
                transaction.account.save()
                account.save()
        account.delete()
        messages.success(request, 'Account and all related transactions deleted and balances reverted!')
        return redirect('accounts')
    return render(request, 'core/delete_account.html', {'account': account})

@user_login_required
def add_transaction_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    accounts = Account.objects.filter(user=user)
    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        account_id = request.POST.get('account')
        to_account_id = request.POST.get('to_account')
        account = get_object_or_404(Account, id=account_id, user=user)
        to_account = None
        from decimal import Decimal
        amount = Decimal(str(amount))
        if transaction_type == 'TRANSFER' and to_account_id:
            to_account = get_object_or_404(Account, id=to_account_id, user=user)
        transaction = Transaction.objects.create(
            user=user,
            account=account,
            to_account=to_account,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            transaction_date=timezone.now().date()
        )
        # Update balances
        if transaction_type == 'INCOME':
            account.balance += amount
            account.save()
        elif transaction_type == 'EXPENSE':
            account.balance -= amount
            account.save()
        elif transaction_type == 'TRANSFER' and to_account:
            account.balance -= amount
            to_account.balance += amount
            account.save()
            to_account.save()
        messages.success(request, 'Transaction added successfully!')
        return redirect('dashboard')
    return render(request, 'core/add_transaction.html', {'accounts': accounts})

@user_login_required
def delete_transaction_view(request, transaction_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('signin')
    user = get_object_or_404(User, id=user_id)
    transaction = get_object_or_404(Transaction, id=transaction_id, user=user)
    if request.method == 'POST':
        # Roll back the transaction effect on account balances
        amount = Decimal(str(transaction.amount))
        if transaction.transaction_type == 'INCOME':
            if transaction.account:
                transaction.account.balance -= amount
                transaction.account.save()
        elif transaction.transaction_type == 'EXPENSE':
            if transaction.account:
                transaction.account.balance += amount
                transaction.account.save()
        elif transaction.transaction_type == 'TRANSFER' and transaction.account and transaction.to_account:
            transaction.account.balance += amount
            transaction.to_account.balance -= amount
            transaction.account.save()
            transaction.to_account.save()
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    return render(request, 'core/delete_transaction.html', {'transaction': transaction})

def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('signin')

@user_login_required
def ajax_change_password(request):
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Not authenticated.'})
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if not check_password(current_password, user.password):
            return JsonResponse({'success': False, 'message': 'Current password is incorrect.'})
        if new_password != confirm_password:
            return JsonResponse({'success': False, 'message': 'New passwords do not match.'})
        user.password = make_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@require_POST
@user_login_required
def add_account_ajax(request):
    try:
        print('add_account_ajax called')
        user_id = request.session.get('user_id')
        print('user_id:', user_id)
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        print('POST data:', data)
        account_name = data.get('account_name', '').strip()
        amount_type = data.get('amount_type', '').strip()
        if not account_name or not amount_type:
            print('Missing fields')
            return JsonResponse({'success': False, 'message': 'All fields are required.'})
        if Account.objects.filter(user=user, account_name=account_name).exists():
            print('Account exists')
            return JsonResponse({'success': False, 'message': 'Account with this name already exists.'})
        account = Account.objects.create(user=user, account_name=account_name, balance=0, amount_type=amount_type)
        print('Account created:', account)
        return JsonResponse({'success': True, 'message': 'Account added successfully.'})
    except Exception as e:
        print('Exception:', e)
        return JsonResponse({'success': False, 'message': 'Error: ' + str(e)})

@user_login_required
def accounts_view(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    accounts = Account.objects.filter(user=user)
    return render(request, 'core/accounts.html', {
        'accounts': accounts,
        'user': user,
        'amount_type_choices': AMOUNT_TYPE_CHOICES,
    })

@require_POST
@user_login_required
def update_balance_ajax(request):
    try:
        user_id = request.session.get('user_id')
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        account_id = data.get('account_id')
        balance = data.get('balance')
        if not account_id or balance is None:
            return JsonResponse({'success': False, 'message': 'Missing data.'})
        try:
            balance = float(balance)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid balance.'})
        account = get_object_or_404(Account, id=account_id, user=user)
        account.balance = balance
        account.save()
        return JsonResponse({'success': True, 'message': 'Balance updated.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error: ' + str(e)})

@require_POST
def add_transaction_ajax(request):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Not authenticated.'})
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        transaction_type = data.get('transaction_type')
        amount = data.get('amount')
        description = data.get('description')
        transaction_date = data.get('transaction_date')
        if not transaction_type or not amount or not description or not transaction_date:
            return JsonResponse({'success': False, 'message': 'All fields are required.'})
        amount = Decimal(str(amount))
        if transaction_type in ['INCOME', 'EXPENSE']:
            account_id = data.get('account_id')
            if not account_id:
                return JsonResponse({'success': False, 'message': 'Account is required.'})
            account = get_object_or_404(Account, id=account_id, user=user)
            transaction = Transaction.objects.create(
                user=user,
                account=account,
                amount=amount,
                description=description,
                transaction_type=transaction_type,
                transaction_date=transaction_date
            )
            if transaction_type == 'INCOME':
                account.balance += amount
            else:
                account.balance -= amount
            account.save()
        elif transaction_type == 'TRANSFER':
            from_account_id = data.get('from_account_id')
            to_account_id = data.get('to_account_id')
            if not from_account_id or not to_account_id or from_account_id == to_account_id:
                return JsonResponse({'success': False, 'message': 'Valid from and to accounts are required.'})
            from_account = get_object_or_404(Account, id=from_account_id, user=user)
            to_account = get_object_or_404(Account, id=to_account_id, user=user)
            transaction = Transaction.objects.create(
                user=user,
                account=from_account,
                to_account=to_account,
                amount=amount,
                description=description,
                transaction_type=transaction_type,
                transaction_date=transaction_date
            )
            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()
        else:
            return JsonResponse({'success': False, 'message': 'Invalid transaction type.'})
        return JsonResponse({'success': True, 'message': 'Transaction added successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error: ' + str(e)})

@require_POST
@csrf_exempt
def delete_transaction_ajax(request, transaction_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Not authenticated.'})
        user = get_object_or_404(User, id=user_id)
        transaction = get_object_or_404(Transaction, id=transaction_id, user=user)
        amount = Decimal(str(transaction.amount))
        # Roll back the transaction effect on account balances
        if transaction.transaction_type == 'INCOME':
            if transaction.account:
                transaction.account.balance -= amount
                transaction.account.save()
        elif transaction.transaction_type == 'EXPENSE':
            if transaction.account:
                transaction.account.balance += amount
                transaction.account.save()
        elif transaction.transaction_type == 'TRANSFER' and transaction.account and transaction.to_account:
            transaction.account.balance += amount
            transaction.to_account.balance -= amount
            transaction.account.save()
            transaction.to_account.save()
        transaction.delete()
        return JsonResponse({'success': True, 'message': 'Transaction deleted successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error: ' + str(e)})

@require_POST
@csrf_exempt
def rename_account_ajax(request, account_id):
    try:
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Not authenticated.'})
        user = get_object_or_404(User, id=user_id)
        account = get_object_or_404(Account, id=account_id, user=user)
        data = json.loads(request.body)
        new_name = data.get('account_name', '').strip()
        if not new_name:
            return JsonResponse({'success': False, 'message': 'Account name is required.'})
        if Account.objects.filter(user=user, account_name=new_name).exclude(id=account_id).exists():
            return JsonResponse({'success': False, 'message': 'Account with this name already exists.'})
        account.account_name = new_name
        account.save()
        return JsonResponse({'success': True, 'message': 'Account renamed successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Error: ' + str(e)})
