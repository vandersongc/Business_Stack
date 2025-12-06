from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa 
import openpyxl 

from .forms import FuncionarioForm
from .models import Funcionario

# human_resources/views.py (Trecho principal atualizado)
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from .models import Funcionario, LancamentoMensal, EventoFolha
import datetime

@login_required
def home_rh(request):
    return render(request, 'home_rh.html')

@login_required
def cadastro_funcionario(request):
    termo_busca = request.GET.get('termo_busca')
    id_editar = request.GET.get('id_editar') 
    resultados = None
    
    if termo_busca:
        resultados = Funcionario.objects.filter(
            Q(nome_completo__icontains=termo_busca) | Q(cpf__icontains=termo_busca)
        )

    funcionario_instance = None
    if id_editar:
        funcionario_instance = get_object_or_404(Funcionario, pk=id_editar)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario_instance)
        if form.is_valid():
            # Logica de Auditoria
            mensagem_log = ""
            acao_flag = ADDITION
            if funcionario_instance:
                acao_flag = CHANGE
                alteracoes = []
                if form.changed_data:
                    for campo in form.changed_data:
                        v_antigo = getattr(funcionario_instance, campo)
                        v_novo = form.cleaned_data.get(campo)
                        alteracoes.append(f"{campo}: {v_antigo} -> {v_novo}")
                    mensagem_log = "Alterações: " + " | ".join(alteracoes)
                else:
                    mensagem_log = "Salvo sem alterações."
            else:
                mensagem_log = "Adicionado via Portal RH"

            funcionario = form.save()
            
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(Funcionario).pk,
                object_id=str(funcionario.pk),
                object_repr=str(funcionario),
                action_flag=acao_flag,
                change_message=mensagem_log 
            )

            messages.success(request, 'Dados salvos com sucesso!')
            return redirect('cadastro_funcionarios')
    else:
        form = FuncionarioForm(instance=funcionario_instance)

    historico = []
    if id_editar:
        ct = ContentType.objects.get_for_model(Funcionario)
        historico = LogEntry.objects.filter(content_type_id=ct.pk, object_id=str(id_editar)).order_by('-action_time')

    return render(request, 'human_resources/cadastro_de_funcionario.html', {
        'form': form, 'resultados': resultados, 'termo_busca': termo_busca,
        'id_editar': id_editar, 'funcionario_editando': funcionario_instance, 'historico': historico
    })

@login_required
def folha_pagamento(request):
    funcionarios = Funcionario.objects.filter(desligado=False)
    total_bruto = sum(f.salario for f in funcionarios if f.salario)
    total_liquido = sum(f.salario_liquido for f in funcionarios if f.salario)

    return render(request, 'human_resources/folha_de_pagamento.html', {
        'funcionarios': funcionarios, 'total_bruto': total_bruto, 'total_liquido': total_liquido
    })

@login_required
def exportar_folha(request, formato):
    funcionarios = Funcionario.objects.filter(desligado=False)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    total_bruto = sum(f.salario for f in funcionarios if f.salario)
    total_liquido = sum(f.salario_liquido for f in funcionarios if f.salario)
    
    if formato == 'xls':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.xlsx"'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Nome', 'CPF', 'Cargo', 'Salário', 'Descontos', 'Líquido'])
        for f in funcionarios:
            ws.append([f.nome_completo, f.cpf, f.cargo, f.salario, f.total_descontos, f.salario_liquido])
        ws.append([]) 
        ws.append(['TOTAIS GERAIS', '', '', total_bruto, '', total_liquido])
        wb.save(response)
        return response

    elif formato == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.txt"'
        lines = [f"FOLHA - {date_str}\n", "-"*90+"\n"]
        lines.append(f"{'NOME':<30} | {'BRUTO':<10} | {'LIQUIDO':<10}\n")
        for f in funcionarios:
            lines.append(f"{f.nome_completo[:30]:<30} | {f.salario:<10} | {f.salario_liquido:<10}\n")
        lines.append("-" * 90 + "\n")
        lines.append(f"{'TOTAIS':<30} | {total_bruto:<10} | {total_liquido:<10}\n")
        response.writelines(lines)
        return response

    elif formato == 'pdf':
        context = {'funcionarios': funcionarios, 'total_bruto': total_bruto, 'total_liquido': total_liquido}
        html = render_to_string('human_resources/folha_pdf_template.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err: return HttpResponse('Erro PDF', status=500)
        return response
    
    return redirect('folha_pagamento')

@login_required
def consulta_contracheque(request):
    termo = request.GET.get('termo_busca')
    res = Funcionario.objects.filter(Q(nome_completo__icontains=termo)|Q(cpf__icontains=termo), desligado=False) if termo else None
    return render(request, 'human_resources/consulta_contracheque.html', {'resultados': res, 'termo_busca': termo})

@login_required
def visualizar_contracheque(request, funcionario_id):
    f = get_object_or_404(Funcionario, pk=funcionario_id)
    context = _get_contracheque_context(f)
    return render(request, 'human_resources/visualizar_contracheque.html', context)

@login_required
def gerar_contracheque_pdf(request, funcionario_id):
    f = get_object_or_404(Funcionario, pk=funcionario_id)
    context = _get_contracheque_context(f)
    html = render_to_string('human_resources/contracheque_pdf_template.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Holerite_{f.nome_completo}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

def _get_contracheque_context(f):
    now = datetime.datetime.now()
    inss = f.calcular_inss()
    irpf = f.calcular_irpf()
    base_irrf = (f.salario or 0) - inss
    return {
        'f': f, 'inss': inss, 'irpf': irpf, 'base_irrf': base_irrf,
        'fgts': f.fgts_mes, 'mes_referencia': now.strftime("%m/%Y"), 'data_emissao': now
    }

# FUNÇÕES AUXILIARES DE CÁLCULO (Agora aceitam um valor base dinâmico)
def calcular_inss_sobre_base(base_calculo):
    teto = Decimal('7786.02')
    if base_calculo > teto: return Decimal('908.85')
    
    desc = Decimal(0)
    faixas = [
        (Decimal('1412.00'), Decimal('0.075')),
        (Decimal('2666.68'), Decimal('0.09')),
        (Decimal('4000.03'), Decimal('0.12')),
        (teto, Decimal('0.14'))
    ]
    base_anterior = Decimal(0)
    for limite, aliquota in faixas:
        if base_calculo > base_anterior:
            base_faixa = min(base_calculo, limite) - base_anterior
            desc += base_faixa * aliquota
            base_anterior = limite
        else:
            break
    return desc

def calcular_irpf_sobre_base(base_tributavel):
    # Tabela 2024/2025 simplificada
    if base_tributavel <= Decimal('2259.20'): return Decimal(0)
    elif base_tributavel <= Decimal('2826.65'): return (base_tributavel * Decimal('0.075')) - Decimal('169.44')
    elif base_tributavel <= Decimal('3751.05'): return (base_tributavel * Decimal('0.15')) - Decimal('381.44')
    elif base_tributavel <= Decimal('4664.68'): return (base_tributavel * Decimal('0.225')) - Decimal('662.77')
    else: return (base_tributavel * Decimal('0.275')) - Decimal('896.00')

def _get_contracheque_context(f):
    now = datetime.datetime.now()
    mes_ref = now.strftime("%m/%Y") # Ex: "12/2025"
    
    # 1. Recuperar eventos variáveis lançados para este mês
    lancamentos = LancamentoMensal.objects.filter(funcionario=f, mes_referencia=mes_ref)
    
    # 2. Compor a lista de itens do holerite
    itens_holerite = []
    
    # Adiciona Salário Base (Evento fixo)
    itens_holerite.append({
        'codigo': '001', 'descricao': 'SALARIO BASE', 'ref': '30d', 
        'vencimento': f.salario, 'desconto': Decimal(0)
    })
    
    total_vencimentos = f.salario or Decimal(0)
    total_descontos = Decimal(0)
    base_inss = f.salario or Decimal(0)
    
    # Processa lançamentos variáveis (ex: Hora Extra)
    for l in lancamentos:
        if l.evento.tipo == 'V':
            itens_holerite.append({'codigo': l.evento.codigo, 'descricao': l.evento.nome, 'ref': l.quantidade or '-', 'vencimento': l.valor, 'desconto': 0})
            total_vencimentos += l.valor
            if l.evento.incide_inss: base_inss += l.valor
        else:
            itens_holerite.append({'codigo': l.evento.codigo, 'descricao': l.evento.nome, 'ref': l.quantidade or '-', 'vencimento': 0, 'desconto': l.valor})
            total_descontos += l.valor

    # 3. Calcular Impostos Dinamicamente
    val_inss = calcular_inss_sobre_base(base_inss)
    if val_inss > 0:
        itens_holerite.append({'codigo': '901', 'descricao': 'INSS', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_inss})
        total_descontos += val_inss

    base_irrf = base_inss - val_inss # Simplificado (sem dependentes por enqto)
    val_irrf = calcular_irpf_sobre_base(base_irrf)
    if val_irrf > 0:
        itens_holerite.append({'codigo': '911', 'descricao': 'IRRF', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_irrf})
        total_descontos += val_irrf

    # Adicionar descontos fixos antigos (Vale transporte etc) para não perder lógica
    # Idealmente, você migraria isso para EventoFolha com o tempo
    fixos = [
        ('920', 'VALE TRANSPORTE', f.desc_vale_transporte),
        ('921', 'VALE ALIMENTACAO', f.desc_vale_alimentacao),
        ('922', 'ASSIST. MEDICA', f.desc_assist_medica)
    ]
    for cod, desc, val in fixos:
        if val > 0:
            itens_holerite.append({'codigo': cod, 'descricao': desc, 'ref': '-', 'vencimento': 0, 'desconto': val})
            total_descontos += val

    liquido = total_vencimentos - total_descontos

    return {
        'f': f,
        'mes_referencia': mes_ref,
        'itens_holerite': itens_holerite,
        'total_vencimentos': total_vencimentos,
        'total_descontos': total_descontos,
        'liquido': liquido,
        'bases': {'inss': base_inss, 'fgts': base_inss, 'irrf': base_irrf}
    }