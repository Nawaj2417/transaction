from django.urls import path
from .views import UserCreateView
from rest_framework_simplejwt import views as jwt_views
from .views import (
    TransactionListCreate,
    TransactionDetail,
    PDFTransactionListView,
    PDFTransactionDetailView
)

urlpatterns = [
    path('transactions/', TransactionListCreate.as_view(), name='transaction-list-create'),
    path('transactions/<str:transaction_id>/', TransactionDetail.as_view(), name='transaction-detail'),
    path('pdf/transactions/', PDFTransactionListView.as_view(), name='pdf-transaction-list'),
    path('pdf/transactions/<str:txnid>/', PDFTransactionDetailView.as_view(), name='pdf-transaction-detail'),
    path('users/', UserCreateView.as_view(), name='user-create'),

        # JWT token endpoints
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
