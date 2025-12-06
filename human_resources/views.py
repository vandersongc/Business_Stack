from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
import csv
import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa # Requer: pip install xhtml2pdf
import openpyxl # Requer: pip install openpyxl
from django.template.loader import render_to_string

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

@login_required
def folha_pagamento(request):
    # Filtra apenas funcionários ATIVOS (não desligados)
    funcionarios = Funcionario.objects.filter(desligado=False)
    
    total_bruto = sum(f.salario for f in funcionarios if f.salario)
    total_liquido = sum(f.salario_liquido for f in funcionarios if f.salario)

    return render(request, 'human_resources/folha_de_pagamento.html', {
        'funcionarios': funcionarios,
        'total_bruto': total_bruto,
        'total_liquido': total_liquido
    })

@login_required
def exportar_folha(request, formato):
    funcionarios = Funcionario.objects.filter(desligado=False)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # --- CÁLCULO DOS TOTAIS GERAIS ---
    total_bruto = sum(f.salario for f in funcionarios if f.salario)
    total_liquido = sum(f.salario_liquido for f in funcionarios if f.salario)
    
    # --- EXPORTAR EXCEL (XLS) ---
    if formato == 'xls':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Folha_Pagamento_{date_str}.xlsx"'
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Folha de Pagamento"
        
        # Cabeçalho
        ws.append(['Nome', 'CPF', 'Cargo', 'Salário Bruto', 'Descontos', 'Salário Líquido'])
        
        # Dados
        for f in funcionarios:
            ws.append([
                f.nome_completo, 
                f.cpf, 
                f.cargo, 
                f.salario, 
                f.calculo_descontos, 
                f.salario_liquido
            ])
            
        # Linha de Totais (Pula uma linha e adiciona o total)
        ws.append([]) 
        ws.append(['TOTAIS GERAIS', '', '', total_bruto, '', total_liquido])
            
        wb.save(response)
        return response

    # --- EXPORTAR TXT ---
    elif formato == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="Folha_Pagamento_{date_str}.txt"'
        
        lines = []
        lines.append(f"FOLHA DE PAGAMENTO - {date_str}\n")
        lines.append("=" * 95 + "\n")
        lines.append(f"{'NOME':<30} | {'CPF':<14} | {'BRUTO':<12} | {'DESC.':<12} | {'LÍQUIDO':<12}\n")
        lines.append("-" * 95 + "\n")
        
        for f in funcionarios:
            line = f"{f.nome_completo[:30]:<30} | {f.cpf:<14} | R$ {f.salario:<9} | R$ {f.calculo_descontos:<9} | R$ {f.salario_liquido:<9}\n"
            lines.append(line)
            
        lines.append("-" * 95 + "\n")
        lines.append(f"{'TOTAIS GERAIS':<47} | R$ {total_bruto:<9} | {'':<12} | R$ {total_liquido:<9}\n")
            
        response.writelines(lines)
        return response

    # --- EXPORTAR PDF ---
    elif formato == 'pdf':
        # Passamos os totais para o template
        context = {
            'funcionarios': funcionarios,
            'total_bruto': total_bruto,
            'total_liquido': total_liquido
        }
        html_string = render_to_string('human_resources/folha_pdf_template.html', context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Folha_Pagamento_{date_str}.pdf"'
        
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('Erro ao gerar PDF', status=500)
        return response

    return redirect('folha_pagamento')

    # ContraCheque

@login_required
def consulta_contracheque(request):
    # --- Lógica de Busca (Reaproveitando padrão) ---
    termo_busca = request.GET.get('termo_busca')
    resultados = None
    
    if termo_busca:
        resultados = Funcionario.objects.filter(
            Q(nome_completo__icontains=termo_busca) | Q(cpf__icontains=termo_busca),
            desligado=False # Apenas ativos
        )
    
    return render(request, 'human_resources/consulta_contracheque.html', {
        'resultados': resultados,
        'termo_busca': termo_busca
    })

# ... imports existentes ...

@login_required
def visualizar_contracheque(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    date_str = datetime.datetime.now()
    
    # Prepara os dados calculados
    inss = funcionario.calcular_inss()
    irpf = funcionario.calcular_irpf()
    
    context = {
        'f': funcionario,
        'inss': inss,
        'irpf': irpf,
        'total_descontos': inss + irpf,
        'mes_referencia': date_str.strftime("%m/%Y"),
        'data_emissao': date_str
    }
    
    return render(request, 'human_resources/visualizar_contracheque.html', context)

@login_required
def gerar_contracheque_pdf(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    date_str = datetime.datetime.now()
    
    # Mesmos cálculos para o PDF ficar igual à tela
    inss = funcionario.calcular_inss()
    irpf = funcionario.calcular_irpf()
    
    context = {
        'f': funcionario,
        'inss': inss,
        'irpf': irpf,
        'total_descontos': inss + irpf,
        'mes_referencia': date_str.strftime("%m/%Y"),
        'hoje': date_str
    }
    
    html_string = render_to_string('human_resources/contracheque_pdf_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    filename = f"Holerite_{funcionario.nome_completo}_{date_str.strftime('%m-%Y')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response