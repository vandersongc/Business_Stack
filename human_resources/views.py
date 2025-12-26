from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils import timezone
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
import csv 
from .forms import FuncionarioForm
from .models import Funcionario, LancamentoMensal

# --- VIEWS DE NAVEGAÇÃO E CADASTRO ---

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

# --- FUNÇÕES DE CÁLCULO ---

def calcular_inss_sobre_base(base_calculo):
    teto = Decimal('7786.02')
    base_calculo = base_calculo or Decimal(0)
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
            
    # Ajuste fino para bater com tabelas progressivas padrão
    if base_calculo <= 1412.00: return base_calculo * Decimal('0.075')
    elif base_calculo <= 2666.68: return (base_calculo * Decimal('0.09')) - Decimal('21.18')
    elif base_calculo <= 4000.03: return (base_calculo * Decimal('0.12')) - Decimal('101.18')
    elif base_calculo <= 7786.02: return (base_calculo * Decimal('0.14')) - Decimal('181.18')
    else: return Decimal('908.85')

def calcular_irpf_sobre_base(base_tributavel):
    base_tributavel = base_tributavel or Decimal(0)
    if base_tributavel <= Decimal('2259.20'): return Decimal(0)
    elif base_tributavel <= Decimal('2826.65'): return (base_tributavel * Decimal('0.075')) - Decimal('169.44')
    elif base_tributavel <= Decimal('3751.05'): return (base_tributavel * Decimal('0.15')) - Decimal('381.44')
    elif base_tributavel <= Decimal('4664.68'): return (base_tributavel * Decimal('0.225')) - Decimal('662.77')
    else: return (base_tributavel * Decimal('0.275')) - Decimal('896.00')

def _get_contracheque_context(f):
    now = datetime.datetime.now()
    mes_ref = now.strftime("%m/%Y")
    
    lancamentos = LancamentoMensal.objects.filter(funcionario=f, mes_referencia=mes_ref)
    
    itens_holerite = []
    
    # Salário Base
    itens_holerite.append({
        'codigo': '001', 'descricao': 'SALARIO BASE', 'ref': '30d', 
        'vencimento': f.salario, 'desconto': Decimal(0)
    })
    
    total_vencimentos = f.salario or Decimal(0)
    total_descontos = Decimal(0)
    base_inss = f.salario or Decimal(0)
    
    # Eventos variáveis
    for l in lancamentos:
        if l.evento.tipo == 'V':
            itens_holerite.append({
                'codigo': l.evento.codigo, 'descricao': l.evento.nome, 
                'ref': l.quantidade or '-', 'vencimento': l.valor, 'desconto': 0
            })
            total_vencimentos += l.valor
            if l.evento.incide_inss: base_inss += l.valor
        else:
            itens_holerite.append({
                'codigo': l.evento.codigo, 'descricao': l.evento.nome, 
                'ref': l.quantidade or '-', 'vencimento': 0, 'desconto': l.valor
            })
            total_descontos += l.valor

    # Impostos
    val_inss = calcular_inss_sobre_base(base_inss)
    if val_inss > 0:
        itens_holerite.append({'codigo': '901', 'descricao': 'INSS', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_inss})
        total_descontos += val_inss

    base_irrf = base_inss - val_inss 
    val_irrf = calcular_irpf_sobre_base(base_irrf)
    if val_irrf > 0:
        itens_holerite.append({'codigo': '911', 'descricao': 'IRRF', 'ref': 'Tab.', 'vencimento': 0, 'desconto': val_irrf})
        total_descontos += val_irrf

    # Fixos
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

    salario_liquido = total_vencimentos - total_descontos

    return {
        'f': f,
        'mes_referencia': mes_ref,
        'data_emissao': now,
        'itens_holerite': itens_holerite,
        'total_vencimentos': total_vencimentos,
        'total_descontos': total_descontos,
        'salario_liquido': salario_liquido,
        'base_inss': base_inss,
        'base_irrf': base_irrf,
        'fgts': base_inss * Decimal('0.08'),
    }

# --- VIEWS DA FOLHA E CONTRACHEQUE ---

@login_required
def folha_pagamento(request):
    """
    View responsável por exibir a folha de pagamento geral na tela.
    (Esta função estava faltando e causava o erro AttributeError)
    """
    funcionarios = Funcionario.objects.filter(desligado=False)
    dados_folha = []
    
    tg_vencimentos = Decimal(0)
    tg_descontos = Decimal(0)
    tg_liquido = Decimal(0)

    for f in funcionarios:
        ctx = _get_contracheque_context(f)
        dados_folha.append({
            'funcionario': f,
            'total_vencimentos': ctx['total_vencimentos'],
            'total_descontos': ctx['total_descontos'],
            'liquido': ctx['salario_liquido'],
            'cargo': f.cargo
        })
        tg_vencimentos += ctx['total_vencimentos']
        tg_descontos += ctx['total_descontos']
        tg_liquido += ctx['salario_liquido']

    context = {
        'dados_folha': dados_folha,
        'total_geral_vencimentos': tg_vencimentos,
        'total_geral_descontos': tg_descontos,
        'total_geral_liquido': tg_liquido,
        'data_atual': datetime.datetime.now()
    }
    return render(request, 'human_resources/folha_de_pagamento.html', context)

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
            'matricula': f.id, 
            'nome': f.nome_completo,
            'cpf': f.cpf,
            'cargo': f.cargo,
            'bruto': ctx['total_vencimentos'], 
            'desc': ctx['total_descontos'],
            'liq': ctx['salario_liquido']
        })
        tot_bruto += ctx['total_vencimentos']
        tot_liq += ctx['salario_liquido']

    if formato == 'xls':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.xlsx"'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['Matrícula', 'Nome', 'CPF', 'Cargo', 'Salário Bruto', 'Descontos', 'Líquido'])
        for d in dados_processados:
            ws.append([d['matricula'], d['nome'], d['cpf'], d['cargo'], float(d['bruto']), float(d['desc']), float(d['liq'])])
        ws.append([]) 
        ws.append(['TOTAIS GERAIS', '', '', '', float(tot_bruto), '', float(tot_liq)])
        wb.save(response)
        return response

    elif formato == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="Folha_{date_str}.txt"'
        lines = [f"FOLHA - {date_str}\n", "="*100+"\n"]
        lines.append(f"{'MAT':<5} | {'NOME':<30} | {'BRUTO':<12} | {'LIQUIDO':<12}\n")
        lines.append("-" * 100 + "\n")
        
        for d in dados_processados:
            lines.append(f"{str(d['matricula']):<5} | {d['nome'][:30]:<30} | {d['bruto']:>12.2f} | {d['liq']:>12.2f}\n")
            
        lines.append("-" * 100 + "\n")
        lines.append(f"{'TOTAL':<38} | {tot_bruto:>12.2f} | {tot_liq:>12.2f}\n")
        response.writelines(lines)
        return response

    elif formato == 'pdf':
        context = {
            'dados_folha': dados_processados, 
            'total_geral_vencimentos': tot_bruto,
            'total_geral_liquido': tot_liq,
            'data_atual': datetime.datetime.now()
        }
        
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

# --- GERAÇÃO DE CRACHÁ ---
@login_required
def gerar_cracha(request, funcionario_id):
    funcionario = get_object_or_404(Funcionario, pk=funcionario_id)
    
    context = {'funcionario': funcionario}
    html = render_to_string('human_resources/cracha_template.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Cracha_{funcionario.nome_completo}.pdf"'
    
    # Cria o PDF (Crachá tamanho padrão CR80: 85.6mm x 54mm)
    pisa.CreatePDF(html, dest=response)
    return response

# --- LEITOR DE PONTO (Front-end da Câmera) ---
@login_required
def painel_ponto(request):
    return render(request, 'human_resources/painel_ponto.html')

# --- API DE REGISTRO DE PONTO (Back-end) ---
@csrf_exempt
def registrar_ponto_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_content = data.get('qr_content') # Ex: "FUNC-1"
            
            # Extrai o ID
            if not qr_content or not qr_content.startswith("FUNC-"):
                return JsonResponse({'status': 'error', 'message': 'QR Code inválido.'})
            
            func_id = qr_content.split('-')[1]
            funcionario = Funcionario.objects.get(id=func_id)
            
            hoje = timezone.now().date()
            agora = timezone.now().time()
            
            # Busca ou cria o registro do dia
            ponto, created = RegistroPonto.objects.get_or_create(
                funcionario=funcionario,
                data=hoje
            )
            
            mensagem = ""
            
            # Lógica simples de preenchimento sequencial
            if not ponto.entrada_1:
                ponto.entrada_1 = agora
                mensagem = f"Entrada registrada às {agora.strftime('%H:%M')}"
            elif not ponto.saida_1:
                ponto.saida_1 = agora
                mensagem = f"Saída Almoço registrada às {agora.strftime('%H:%M')}"
            elif not ponto.entrada_2:
                ponto.entrada_2 = agora
                mensagem = f"Retorno Almoço registrado às {agora.strftime('%H:%M')}"
            elif not ponto.saida_2:
                ponto.saida_2 = agora
                mensagem = f"Saída Expediente registrada às {agora.strftime('%H:%M')}"
            else:
                return JsonResponse({'status': 'warning', 'message': 'Todos os pontos do dia já registrados.'})
            
            ponto.save()
            return JsonResponse({'status': 'success', 'message': mensagem, 'funcionario': funcionario.nome_completo})
            
        except Funcionario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Funcionário não encontrado.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'})

def processar_faltas_mensal(request):
    """
    Verifica dias úteis passados sem registro de ponto e cria lançamentos de desconto.
    """
    if not request.user.is_staff:
        return redirect('home')

    hoje = timezone.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Busca ou cria o Evento de Falta
    evento_falta, _ = EventoFolha.objects.get_or_create(
        codigo='999',
        defaults={'nome': 'FALTA NAO JUSTIFICADA', 'tipo': 'D', 'incide_inss': True, 'incide_irrf': True, 'incide_fgts': True}
    )

    funcionarios = Funcionario.objects.filter(desligado=False)
    count_faltas = 0

    import calendar
    # Itera sobre os dias do mês até ontem
    for dia_num in range(1, hoje.day): 
        data_verificar = hoje.replace(day=dia_num)
        
        # Se for sábado (5) ou domingo (6), pula (ajuste conforme regra da empresa)
        if data_verificar.weekday() >= 5:
            continue

        for func in funcionarios:
            # Verifica se existe ponto ou se está de férias
            ponto_existe = RegistroPonto.objects.filter(funcionario=func, data=data_verificar).exists()
            ferias = ControleFerias.objects.filter(funcionario=func, periodo_aquisitivo_inicio__lte=data_verificar, periodo_aquisitivo_fim__gte=data_verificar).exists()
            
            if not ponto_existe and not ferias:
                # É Falta! Calcula o valor do dia (Salário / 30)
                valor_dia = func.salario / Decimal(30)
                
                # Cria ou atualiza o lançamento no contracheque
                mes_ref = data_verificar.strftime("%m/%Y")
                
                # Verifica se já lançamos essa falta para não duplicar no mesmo mês/evento
                # Aqui simplificamos somando ao lançamento existente ou criando um novo
                lancamento, created = LancamentoMensal.objects.get_or_create(
                    funcionario=func,
                    evento=evento_falta,
                    mes_referencia=mes_ref,
                    defaults={'valor': 0, 'quantidade': 0}
                )
                
                # Atenção: Esta lógica é simplificada. O ideal é ter uma tabela de "Ocorrências" separada antes de consolidar na folha.
                # Mas para este exemplo, vamos adicionar o valor se ele ainda não "parece" ter sido processado (ex: rodar script uma vez por dia)
                # Para evitar duplicação real, precisaríamos checar uma tabela de 'FaltasDiarias'.
                
                # Sugestão de uso manual: O RH clica num botão "Calcular Faltas do Mês" e o sistema limpa os lançamentos de falta e recalcula tudo.
                pass 
    
    # Implementação de Recálculo Seguro (Limpa anteriores e insere novos):
    # 1. Apaga descontos de falta do mês atual
    mes_ref_atual = hoje.strftime("%m/%Y")
    LancamentoMensal.objects.filter(mes_referencia=mes_ref_atual, evento=evento_falta).delete()

    for func in funcionarios:
        dias_falta = 0
        for dia_num in range(1, hoje.day + 1): # Verifica o mês todo até hoje
            data_loop = hoje.replace(day=dia_num)
            if data_loop.weekday() < 5: # Apenas dias úteis
                ponto = RegistroPonto.objects.filter(funcionario=func, data=data_loop).exists()
                if not ponto:
                    # Verifica férias (implementação simples)
                    em_ferias = False # Implementar verificação de férias aqui
                    if not em_ferias:
                        dias_falta += 1
        
        if dias_falta > 0:
            valor_desconto = (func.salario / Decimal(30)) * Decimal(dias_falta)
            LancamentoMensal.objects.create(
                funcionario=func,
                evento=evento_falta,
                mes_referencia=mes_ref_atual,
                valor=valor_desconto,
                quantidade=dias_falta
            )
            count_faltas += dias_falta

    messages.success(request, f'Processamento concluído. {count_faltas} dias de falta contabilizados.')
    return redirect('folha_pagamento')