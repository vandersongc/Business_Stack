"""
URL configuration for business_stack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views  # Importa as views que acabamos de criar

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Página Inicial
    path('', views.home, name='home'),

    # Rotas dos Módulos (Cards)
    path('administrador/', views.administrador, name='administrador'),
    path('auditoria/', views.auditoria, name='auditoria'),
    path('contabilidade/', views.contabilidade, name='contabilidade'),
    path('financeiro/', views.financeiro, name='financeiro'),
    path('logistica/', views.logistica, name='logistica'),
    path('pessoal/', views.pessoal, name='pessoal'),
    path('suprimentos/', views.suprimentos, name='suprimentos'),

    # Rotas do Menu Superior
    path('contato/', views.contato, name='contato'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('logout/', views.logout_view, name='logout'),
]
