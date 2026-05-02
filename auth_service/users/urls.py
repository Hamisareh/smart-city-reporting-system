# users/urls.py
from django.urls import path
from .views import (
    RegisterView, 
    CreateAdminView, 
    ProfileView, 
    VerifyUserView, 
    CustomLoginView,
    LogoutView,
    RefreshTokenView,
    UserListView,        
    UserDeleteView,      
    UserUpdateView,
    UserDetailView,          
    PublicAdminListView,       
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', CustomLoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('refresh/', RefreshTokenView.as_view()),
    path('create-admin/', CreateAdminView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('verify/', VerifyUserView.as_view()),
    path('users/', UserListView.as_view()),           
    path('users/<int:pk>/', UserDetailView.as_view()),     
    path('users/<int:pk>/delete/', UserDeleteView.as_view()), 
    path('users/<int:pk>/update/', UserUpdateView.as_view()), 
    path('admins/', PublicAdminListView.as_view()),
]