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
# business_stack/urls.py
from django.contrib import admin
from django.urls import path
from home import views as home_views  # Importando da app home
from . import views as temp_views     # Importando as views temporárias (se ainda as usar)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota da Página Inicial (Apontando para a app home)
    path('', home_views.home, name='home'),

    # Rotas dos Módulos (Se ainda não tiver views específicas nas outras apps, pode manter as temporárias)
    path('administrador/', temp_views.administrador, name='administrador'),
    path('auditoria/', temp_views.auditoria, name='auditoria'),
    path('contabilidade/', temp_views.contabilidade, name='contabilidade'),
    path('financeiro/', temp_views.financeiro, name='financeiro'),
    path('logistica/', temp_views.logistica, name='logistica'),
    path('pessoal/', temp_views.pessoal, name='pessoal'),
    path('suprimentos/', temp_views.suprimentos, name='suprimentos'),

    # Menus
    path('contato/', temp_views.contato, name='contato'),
    path('configuracoes/', temp_views.configuracoes, name='configuracoes'),
    path('logout/', temp_views.logout_view, name='logout'),
]