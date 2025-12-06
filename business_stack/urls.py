from django.contrib import admin
from django.urls import path
from home import views as home_views
from human_resources import views as rh_views
from . import views as temp_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', home_views.home, name='home'),
    
    # Rotas de Autenticação
    path('cadastro/', home_views.cadastro, name='cadastro'),
    
    # --- CORREÇÃO AQUI: Use .login_view em vez de .login ---
    path('login/', home_views.login_view, name='login'),
    # -------------------------------------------------------
    
    path('logout/', home_views.logout_view, name='logout'),

   
    path('pessoal/', rh_views.home_rh, name='pessoal'), 
    

    # Rotas dos Módulos (seus outros links)
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
]