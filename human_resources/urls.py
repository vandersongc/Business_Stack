from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Importe as views corretamente
from home import views as home_views
from human_resources import views as rh_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Rota Padrão ---
    path('', home_views.home, name='home'),
    path('login/', home_views.login_view, name='login'),
    path('cadastro/', home_views.cadastro_view, name='cadastro'),
    path('logout/', home_views.logout_view, name='logout'),

    # --- Rotas do RH (Human Resources) ---
    path('pessoal/', rh_views.home_rh, name='pessoal'),
    path('cadastro_funcionarios/', rh_views.cadastro_funcionario, name='cadastro_funcionarios'),
    
    # Folha e Contracheque
    path('folha_pagamento/', rh_views.folha_pagamento, name='folha_pagamento'),
    
    # ESTA É A ROTA QUE CORRIGE O ERRO (Unificada para Excel, TXT e PDF da folha)
    path('folha/exportar/<str:formato>/', rh_views.exportar_folha, name='exportar_folha'),

    # Visualização e PDF individual do funcionário
    path('contracheque/consulta/', rh_views.consulta_contracheque, name='consulta_contracheque'),
    path('contracheque/visualizar/<int:funcionario_id>/', rh_views.visualizar_contracheque, name='visualizar_contracheque'),
    path('contracheque/pdf/<int:funcionario_id>/', rh_views.gerar_contracheque_pdf, name='gerar_contracheque_pdf'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)