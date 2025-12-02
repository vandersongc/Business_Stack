# business_stack/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

# Views temporárias para os botões não darem erro
def administrador(request):
    return render(request, 'base.html', {'content': 'Módulo Administrador (Em construção)'})

def auditoria(request):
    return render(request, 'base.html', {'content': 'Módulo Auditoria (Em construção)'})

def contabilidade(request):
    return render(request, 'base.html', {'content': 'Módulo Contabilidade (Em construção)'})

def financeiro(request):
    # Futuramente você apontará para 'finance.views'
    return render(request, 'base.html', {'content': 'Módulo Financeiro (Em construção)'})

def logistica(request):
    return render(request, 'base.html', {'content': 'Módulo Logística (Em construção)'})

def pessoal(request):
    # Futuramente você apontará para 'human_resources.views'
    return render(request, 'base.html', {'content': 'Módulo Pessoal (Em construção)'})

def suprimentos(request):
    # Futuramente você apontará para 'procurement.views'
    return render(request, 'base.html', {'content': 'Módulo Suprimentos (Em construção)'})

# Views para o menu superior
def contato(request):
    return render(request, 'base.html', {'content': 'Fale Conosco'})

def configuracoes(request):
    return render(request, 'base.html', {'content': 'Configurações'})

def logout_view(request):
    return render(request, 'base.html', {'content': 'Você saiu do sistema.'})