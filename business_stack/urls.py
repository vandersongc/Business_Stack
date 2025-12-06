from django.contrib import admin
from django.urls import path
from home import views as home_views
from human_resources import views as rh_views
from . import views as temp_views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_views.home, name='home'),
    path('cadastro/', home_views.cadastro, name='cadastro'),
    path('login/', home_views.login_view, name='login'),
    path('logout/', home_views.logout_view, name='logout'),

    # RH
    path('pessoal/', rh_views.home_rh, name='pessoal'), 
    path('cadastro_funcionarios/', rh_views.cadastro_funcionario, name='cadastro_funcionarios'),
    path('folha_pagamento/', rh_views.folha_pagamento, name='folha_pagamento'),
    path('exportar_folha/<str:formato>/', rh_views.exportar_folha, name='exportar_folha'),
    
    # Contracheque
    path('contracheque/', rh_views.consulta_contracheque, name='consulta_contracheque'),
    path('contracheque/visualizar/<int:funcionario_id>/', rh_views.visualizar_contracheque, name='visualizar_contracheque'),
    path('contracheque/pdf/<int:funcionario_id>/', rh_views.gerar_contracheque_pdf, name='gerar_contracheque_pdf'),

    # Outros Módulos
    path('administrador/', temp_views.administrador, name='administrador'),
    path('auditoria/', temp_views.auditoria, name='auditoria'),
    path('contabilidade/', temp_views.contabilidade, name='contabilidade'),
    path('financeiro/', temp_views.financeiro, name='financeiro'),
    path('logistica/', temp_views.logistica, name='logistica'),
    path('pessoal_temp/', temp_views.pessoal, name='pessoal_temp'),
    path('suprimentos/', temp_views.suprimentos, name='suprimentos'),
    path('contato/', temp_views.contato, name='contato'),
    path('configuracoes/', temp_views.configuracoes, name='configuracoes'),
]