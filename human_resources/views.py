from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
import datetime
from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa 
import openpyxl 

from .forms import FuncionarioForm
from .models import Funcionario, LancamentoMensal

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
            acao_flag = CHANGE if funcionario_instance else ADDITION
            msg = "Atualização via Sistema RH" if funcionario_instance else "Novo Cadastro via Sistema RH"
            func = form.save()
            LogEntry.objects.log_action(user_id=request.user.id, content_type_id=ContentType.objects.get_for_model(Funcionario).pk, object_id=str(func.pk), object_repr=str(func), action_flag=acao_flag, change_message=msg)
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

# --- FUNÇÕES DE CÁLCULO DINÂMICO ---

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
    # Tabela 2024/2025
    if base_tributavel <= Decimal('2259.20'): return Decimal(0)
    elif base_tributavel <= Decimal('2826.65'): return (base_tributavel * Decimal('0.075')) - Decimal('169.44')
    elif base_tributavel <= Decimal('3751.05'): return (base_tributavel * Decimal('0.15')) - Decimal('381.44')
    elif base_tributavel <= Decimal('4664.68'): return (base_tributavel * Decimal('0.225')) - Decimal('662.77')
    else: return (base_tributavel * Decimal('0.275')) - Decimal('896.00')

def _get_contracheque_context(f):
    now = datetime.datetime.now()
    mes_ref = now.strftime("%m/%Y")
    
    # 1. Recuperar eventos variáveis lançados para este mês
    lancamentos = LancamentoMensal.objects.filter(funcionario=f, mes_referencia=mes_ref)
    
    itens_holerite = []
    
    # Adiciona Salário Base como o primeiro item
    itens_holerite.append({
        'codigo': '001', 
        'descricao': 'SALARIO BASE', 
        'ref': '30d', 
        'vencimento': f.salario, 
        'desconto': Decimal(0)
    })
    
    # Variáveis acumuladoras
    total_vencimentos = f.salario or Decimal(0)
    total_descontos = Decimal(0)
    base_inss = f.salario or Decimal(0)
    
    # 2. Processa lançamentos variáveis (ex: Hora Extra, Atrasos)
    for l in lancamentos:
        if l.evento.tipo == 'V':
            itens_holerite.append({
                'codigo': l.evento.codigo, 
                'descricao': l.evento.nome, 
                'ref': l.quantidade or '-', 
                'vencimento': l.valor, 
                'desconto': 0
            })
            total_vencimentos += l.valor
            if l.evento.incide_inss: 
                base_inss += l.valor
        else:
            itens_holerite.append({
                'codigo': l.evento.codigo, 
                'descricao': l.evento.nome, 
                'ref': l.quantidade or '-', 
                'vencimento': 0, 
                'desconto': l.valor
            })
            total_descontos += l.valor

    # 3. Calcular Impostos (INSS e IRRF)
    val_inss = calcular_inss_sobre_base(base_inss)
    if val_inss > 0:
        itens_holerite.append({'codigo': '901', 'descricao': 'INSS', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_inss})
        total_descontos += val_inss

    base_irrf = base_inss - val_inss 
    val_irrf = calcular_irpf_sobre_base(base_irrf)
    if val_irrf > 0:
        itens_holerite.append({'codigo': '911', 'descricao': 'IRRF', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_irrf})
        total_descontos += val_irrf

    # 4. Adicionar descontos fixos (Benefícios antigos)
    fixos = [
        ('920', 'VALE TRANSPORTE', f.desc_vale_transporte),
        ('921', 'VALE ALIMENTACAO', f.desc_vale_alimentacao),
        ('922', 'ASSIST. MEDICA', f.desc_assist_medica),
        ('923', 'ASSIST. ODONTO', f.desc_assist_odonto)
    ]
    for cod, desc, val in fixos:
        if val > 0:
            itens_holerite.append({'codigo': cod, 'descricao': desc, 'ref': '-', 'vencimento': 0, 'desconto': val})
            total_descontos += val

    # 5. Cálculo Final do Líquido
    salario_liquido = total_vencimentos - total_descontos

    return {
        'f': f,
        'mes_referencia': mes_ref,
        'data_emissao': now,
        'itens_holerite': itens_holerite,
        'total_vencimentos': total_vencimentos,  # Essencial para o total positivo
        'total_descontos': total_descontos,      # Essencial para o total negativo
        'salario_liquido': salario_liquido,      # Essencial para o líquido
        'base_inss': base_inss,
        'base_irrf': base_irrf,
        'fgts': base_inss * Decimal('0.08'),
    }

# --- VIEWS DA FOLHA ---

@login_required
def folha_pagamento(request):
    funcionarios = Funcionario.objects.filter(desligado=False)
    
    # Processa dados para a lista, reutilizando lógica simplificada
    lista_funcionarios = []
    total_bruto_geral = Decimal(0)
    total_liquido_geral = Decimal(0)

    for f in funcionarios:
        ctx = _get_contracheque_context(f)
        bruto = f.salario # Simplificado para lista, ou ctx['total_vencimentos'] se quiser exato
        # Se quiser usar o valor exato calculado com variáveis:
        # bruto = sum(item['vencimento'] for item in ctx['itens_holerite'])
        
        f.total_descontos_calc = ctx['total_descontos']
        f.salario_liquido_calc = ctx['salario_liquido']
        
        total_bruto_geral += bruto
        total_liquido_geral += ctx['salario_liquido']
        lista_funcionarios.append(f)

    return render(request, 'human_resources/folha_de_pagamento.html', {
        'funcionarios': lista_funcionarios, 
        'total_bruto': total_bruto_geral, 
        'total_liquido': total_liquido_geral
    })

@login_required
def exportar_folha(request, formato):
    funcionarios = Funcionario.objects.filter(desligado=False)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    dados_processados = []
    tot_bruto = Decimal(0)
    tot_liq = Decimal(0)

    for f in funcionarios:
        ctx = _get_contracheque_context(f)
        dados_processados.append({
            'nome': f.nome_completo,
            'cpf': f.cpf,
            'cargo': f.cargo,
            'bruto': f.salario,
            'desc': ctx['total_descontos'],
            'liq': ctx['salario_liquido']
        })
        tot_bruto += f.salario or 0
        tot_liq += ctx['salario_liquido']

    if formato == 'xls':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.xlsx"'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Nome', 'CPF', 'Cargo', 'Salário', 'Descontos', 'Líquido'])
        for d in dados_processados:
            ws.append([d['nome'], d['cpf'], d['cargo'], d['bruto'], d['desc'], d['liq']])
        ws.append([]) 
        ws.append(['TOTAIS GERAIS', '', '', tot_bruto, '', tot_liq])
        wb.save(response)
        return response

    elif formato == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.txt"'
        lines = [f"FOLHA - {date_str}\n", "-"*90+"\n"]
        lines.append(f"{'NOME':<30} | {'BRUTO':<10} | {'LIQUIDO':<10}\n")
        for d in dados_processados:
            lines.append(f"{d['nome'][:30]:<30} | {str(d['bruto']):<10} | {str(d['liq']):<10}\n")
        lines.append("-" * 90 + "\n")
        lines.append(f"{'TOTAIS':<30} | {tot_bruto:<10} | {tot_liq:<10}\n")
        response.writelines(lines)
        return response

    elif formato == 'pdf':
        # Nota: Ajustar template PDF para receber os dados calculados se necessário
        # Por simplicidade, enviamos objetos, mas o ideal seria enviar dicionarios processados
        context = {'funcionarios': funcionarios, 'total_bruto': tot_bruto, 'total_liquido': tot_liq} 
        # ATENÇÃO: O template PDF atual pode precisar de ajustes pois 'f.total_descontos' agora é um método property no model antigo
        # mas aqui estamos calculando dinamicamente. Recomenda-se atualizar o template PDF também.
        
        html = render_to_string('human_resources/folha_pdf_template.html', context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.pdf"'
        pisa.CreatePDF(html, dest=response)
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