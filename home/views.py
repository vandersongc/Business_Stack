from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import CadastroForm

def home(request):
    return render(request, 'index.html')

def cadastro(request):
    if request.method == 'POST':
        # Troque UserCreationForm por CadastroForm aqui
        form = CadastroForm(request.POST) 
        if form.is_valid():
            user = form.save()
            
            # --- LÓGICA DE GRUPOS ---
            grupo_usuario, created = Group.objects.get_or_create(name='Usuário')
            Group.objects.get_or_create(name='Gestor')
            user.groups.add(grupo_usuario)
            
            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('login')
    else:
        # E troque UserCreationForm por CadastroForm aqui também
        form = CadastroForm()
        
    return render(request, 'cadastro.html', {'form': form})

def login_view(request):
    # Nota: O Django usa uma view padrão para login, mas se você quiser
    # manter a sua customizada, precisará usar a lógica de autenticação aqui.
    # Por enquanto, vou redirecionar para a view de login padrão do Django se configurada,
    # ou renderizar seu template. Para simplificar, mantemos o render:
    from django.contrib.auth.views import LoginView
    return LoginView.as_view(template_name='login.html')(request)

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu do sistema.')
    return redirect('login')