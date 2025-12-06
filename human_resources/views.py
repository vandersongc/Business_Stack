from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from .forms import FuncionarioForm
from .models import Funcionario

@login_required
def home_rh(request):
    return render(request, 'home_rh.html')

@login_required
def cadastro_funcionario(request):
    # --- 1. Recuperar parâmetros (Busca e Edição) ---
    termo_busca = request.GET.get('termo_busca')
    id_editar = request.GET.get('id_editar') 

    # --- 2. Lógica de Busca ---
    resultados = None
    if termo_busca:
        resultados = Funcionario.objects.filter(
            Q(nome_completo__icontains=termo_busca) | Q(cpf__icontains=termo_busca)
        )

    # --- 3. Verificar se é Edição ou Novo Cadastro ---
    funcionario_instance = None
    if id_editar:
        funcionario_instance = get_object_or_404(Funcionario, pk=id_editar)

    # --- 4. Processar o Formulário (Salvar) ---
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario_instance)
        
        if form.is_valid():
            # --- DETECÇÃO DE MUDANÇAS (ANTES DE SALVAR) ---
            mensagem_log = ""
            acao_flag = ADDITION

            if funcionario_instance:
                acao_flag = CHANGE
                alteracoes = []
                
                # 'changed_data' é uma lista que o Django cria com os campos que mudaram
                if form.changed_data:
                    for campo in form.changed_data:
                        # Pega o valor antigo (do banco de dados)
                        valor_antigo = getattr(funcionario_instance, campo)
                        
                        # Pega o valor novo (do formulário limpo)
                        valor_novo = form.cleaned_data.get(campo)
                        
                        # Formata a mensagem bonita
                        # Ex: "salario: 2000 -> 3000"
                        alteracoes.append(f"{campo}: {valor_antigo} ➔ {valor_novo}")
                    
                    mensagem_log = "Alterações: " + " | ".join(alteracoes)
                else:
                    mensagem_log = "Salvo sem alterações."
            else:
                mensagem_log = "Adicionado via Portal RH"

            # --- SALVAR NO BANCO ---
            funcionario = form.save()
            
            # --- GRAVAR HISTÓRICO DETALHADO ---
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(Funcionario).pk,
                object_id=str(funcionario.pk),
                object_repr=str(funcionario),
                action_flag=acao_flag,
                change_message=mensagem_log # Aqui entra nossa mensagem detalhada
            )

            if funcionario_instance:
                messages.success(request, 'Dados atualizados com sucesso!')
            else:
                messages.success(request, 'Funcionário cadastrado com sucesso!')
                
            return redirect('cadastro_funcionarios')
    else:
        form = FuncionarioForm(instance=funcionario_instance)

    # --- 5. Buscar Histórico para exibir na tela (Opcional) ---
    historico = []
    if id_editar:
        content_type = ContentType.objects.get_for_model(Funcionario)
        historico = LogEntry.objects.filter(
            content_type_id=content_type.pk,
            object_id=str(id_editar)
        ).select_related('user').order_by('-action_time')

    return render(request, 'human_resources/cadastro_de_funcionario.html', {
        'form': form,
        'resultados': resultados,
        'termo_busca': termo_busca,
        'id_editar': id_editar,
        'funcionario_editando': funcionario_instance,
        'historico': historico
    })