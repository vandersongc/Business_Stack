from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import FuncionarioForm  # Certifique-se de importar o form

@login_required
def home_rh(request):
    return render(request, 'home_rh.html')

def cadastro_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('pessoal')
    # CORREÇÃO AQUI: Use 'else:' em vez de 'elif:'
    else:
        form = FuncionarioForm()

    return render(request, 'human_resources/cadastro_funcionario.html', {'form': form})