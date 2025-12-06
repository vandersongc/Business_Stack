from django.contrib import admin
from django.urls import path
from home import views as home_views
from human_resources import views as rh_views
from . import views as temp_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', home_views.home, name='home'),
    
    # Rota de cadastro
    path('cadastro/', home_views.cadastro, name='cadastro'),
    
    # --- Rotas de Login e Logout ---
    path('login/', home_views.login_view, name='login'),
    path('logout/', home_views.logout_view, name='logout'),

    # --- Rotas de RH ---
    path('pessoal/', rh_views.home_rh, name='pessoal'), 
    path('cadastro_funcionarios/', rh_views.cadastro_funcionario, name='cadastro_funcionarios'),
    
    # Rotas dos Módulos (seus outros links)
    path('administrador/', temp_views.administrador, name='administrador'),
    path('auditoria/', temp_views.auditoria, name='auditoria'),
    path('contabilidade/', temp_views.contabilidade, name='contabilidade'),
    path('financeiro/', temp_views.financeiro, name='financeiro'),
    path('logistica/', temp_views.logistica, name='logistica'),
    path('pessoal_temp/', temp_views.pessoal, name='pessoal_temp'), # Renomeei para evitar conflito de nome com a rota 'pessoal' acima
    path('suprimentos/', temp_views.suprimentos, name='suprimentos'),

    # Menus
    path('contato/', temp_views.contato, name='contato'),
    path('configuracoes/', temp_views.configuracoes, name='configuracoes'),
]