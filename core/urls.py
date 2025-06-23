from django.urls import path
from . import views

urlpatterns = [
    path('', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-account/', views.add_account_view, name='add_account'),
    path('delete-account/<int:account_id>/', views.delete_account_view, name='delete_account'),
    path('add-transaction/', views.add_transaction_view, name='add_transaction'),
    path('delete-transaction/<int:transaction_id>/', views.delete_transaction_view, name='delete_transaction'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
] 