from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from .forms import FuncionarioForm
from .models import Funcionario

@login_required
def home_rh(request):
    return render(request, 'home_rh.html')

@login_required
def cadastro_funcionario(request):
    # --- 1. Parâmetros da URL ---
    termo_busca = request.GET.get('termo_busca')
    id_editar = request.GET.get('id_editar') # Novo parâmetro para saber quem editar

    # --- 2. Lógica de Busca ---
    resultados = None
    if termo_busca:
        resultados = Funcionario.objects.filter(
            Q(nome_completo__icontains=termo_busca) | Q(cpf__icontains=termo_busca)
        )

    # --- 3. Determinar Instância (Novo ou Existente) ---
    funcionario_instance = None
    if id_editar:
        # Se tem ID na URL, buscamos o funcionário no banco para preencher o formulário
        funcionario_instance = get_object_or_404(Funcionario, pk=id_editar)

    # --- 4. Processamento do Formulário (Salvar) ---
    if request.method == 'POST':
        # Se instance for passado, o Django ATUALIZA. Se for None, ele CRIA.
        form = FuncionarioForm(request.POST, instance=funcionario_instance)
        
        if form.is_valid():
            form.save()
            
            # Mensagem personalizada
            if funcionario_instance:
                messages.success(request, 'Dados do funcionário atualizados com sucesso!')
            else:
                messages.success(request, 'Funcionário cadastrado com sucesso!')
                
            return redirect('cadastro_funcionarios')
    else:
        # No GET, preenchemos o formulário com os dados (se estiver editando) ou deixamos vazio
        form = FuncionarioForm(instance=funcionario_instance)

    return render(request, 'human_resources/cadastro_de_funcionario.html', {
        'form': form,
        'resultados': resultados,
        'termo_busca': termo_busca,
        'id_editar': id_editar, # Enviamos para o HTML saber se estamos editando
        'funcionario_editando': funcionario_instance
    })