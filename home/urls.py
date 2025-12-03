from django.urls import path
from home import views


urlpatterns = [
path('', home_views.home, name='home'),
path('cadastro/', views.cadastro, name='cadastro'),
path('login/', views.login_view, name='login'),

]