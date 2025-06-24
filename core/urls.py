from django.urls import path
from . import views

urlpatterns = [
    path('', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', views.accounts_view, name='accounts'),
    path('delete-account/<int:account_id>/', views.delete_account_view, name='delete_account'),
    path('delete-transaction/<int:transaction_id>/', views.delete_transaction_view, name='delete_transaction'),
    path('logout/', views.logout_view, name='logout'),
    path('ajax/change-password/', views.ajax_change_password, name='ajax_change_password'),
    path('ajax/add-account/', views.add_account_ajax, name='add_account_ajax'),
    path('ajax/update-balance/', views.update_balance_ajax, name='update_balance_ajax'),
    path('ajax/add-transaction/', views.add_transaction_ajax, name='add_transaction_ajax'),
    path('ajax/delete-transaction/<int:transaction_id>/', views.delete_transaction_ajax, name='delete_transaction_ajax'),
    path('ajax/rename-account/<int:account_id>/', views.rename_account_ajax, name='rename_account_ajax'),
    path('ajax/get-transaction/<int:transaction_id>/', views.get_transaction_ajax, name='get_transaction_ajax'),
    path('ajax/edit-transaction/<int:transaction_id>/', views.edit_transaction_ajax, name='edit_transaction_ajax'),
] 