from django.urls import path
from . import views
from .views import SignUp

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('register/',views.createUser,name="register"),
    path('verify/',views.verifyUser,name="verify"),
    path('login/',views.login_function,name="login"),
    path('success/',views.success,name="success"),
    path('logout/',views.logout_function,name='logout')
]