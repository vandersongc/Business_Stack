from django.contrib import admin
from django.urls import path
from home import views as home_views
from . import views as temp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota da Página Inicial
    path('', home_views.home, name='home'),

    # --- ROTAS DE AUTENTICAÇÃO (Adicione isto) ---
    path('cadastro/', home_views.cadastro, name='cadastro'),
    path('login/', home_views.login, name='login'),
    # ---------------------------------------------

    # Rotas dos Módulos (Views temporárias)
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