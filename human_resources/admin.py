from django.contrib import admin
from .models import (
    Funcionario, Dependente, HistoricoCargoSalario, 
    EventoFolha, LancamentoMensal, RegistroPonto, ControleFerias
)

class DependenteInline(admin.TabularInline):
    model = Dependente
    extra = 0

class LancamentoInline(admin.TabularInline):
    model = LancamentoMensal
    extra = 0

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'departamento', 'cargo', 'salario', 'desligado')
    search_fields = ('nome_completo', 'cpf', 'email')
    list_filter = ('departamento', 'desligado', 'tipo_contrato')
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'data_nascimento', 'email', 'telefone', 'estado_civil')
        }),
        ('Dados Contratuais', {
            'fields': ('cargo', 'departamento', 'lotacao', 'data_admissao', 'salario', 'tipo_contrato')
        }),
        ('Dados Bancários', {
            'fields': ('banco', 'agencia', 'conta')
        }),
        ('Descontos Fixos (Legado)', {
            'fields': ('desc_vale_transporte', 'desc_vale_alimentacao', 'desc_assist_medica', 'desc_assist_odonto'),
            'classes': ('collapse',)
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'uf')
        }),
        ('Status', {
            'fields': ('desligado', 'data_desligamento')
        }),
    )
    inlines = [DependenteInline, LancamentoInline]

@admin.register(EventoFolha)
class EventoFolhaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo', 'incide_inss', 'incide_irrf', 'incide_fgts')
    ordering = ('codigo',)
    search_fields = ('nome', 'codigo')

@admin.register(LancamentoMensal)
class LancamentoMensalAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'evento', 'mes_referencia', 'valor')
    list_filter = ('mes_referencia', 'evento')
    search_fields = ('funcionario__nome_completo',)

@admin.register(RegistroPonto)
class PontoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'entrada_1', 'saida_2', 'horas_extras')
    list_filter = ('data', 'funcionario')

admin.site.register(HistoricoCargoSalario)
admin.site.register(ControleFerias)