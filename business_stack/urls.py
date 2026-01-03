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

    # === MÓDULO PESSOAL (RH) ===
    # Menu Principal do RH
    path('pessoal/', rh_views.home_rh, name='pessoal'), 
    
    # Funcionalidades de Cadastro e Folha
    path('pessoal/funcionarios/', rh_views.cadastro_funcionario, name='cadastro_funcionarios'),
    path('pessoal/folha/', rh_views.folha_pagamento, name='folha_pagamento'),
    path('pessoal/folha/exportar/<str:formato>/', rh_views.exportar_folha, name='exportar_folha'),
    path('pessoal/folha/processar_faltas/', rh_views.processar_faltas_mensal, name='processar_faltas'),
    
    # Contracheque
    path('pessoal/contracheque/', rh_views.consulta_contracheque, name='consulta_contracheque'),
    path('pessoal/contracheque/visualizar/<int:funcionario_id>/', rh_views.visualizar_contracheque, name='visualizar_contracheque'),
    path('pessoal/contracheque/pdf/<int:funcionario_id>/', rh_views.gerar_contracheque_pdf, name='gerar_contracheque_pdf'),

    # NOVAS FUNCIONALIDADES (Crachá e Ponto)
    # Note que coloquei 'pessoal/' na frente para manter organizado
    path('pessoal/cracha/<int:funcionario_id>/', rh_views.gerar_cracha, name='gerar_cracha'),
    path('pessoal/ponto/painel/', rh_views.painel_ponto, name='painel_ponto'),
    path('pessoal/api/registrar_ponto/', rh_views.registrar_ponto_api, name='registrar_ponto_api'),

    # === OUTROS MÓDULOS (Temporários/Placeholders) ===
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