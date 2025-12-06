# human_resources/admin.py
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
    search_fields = ('nome_completo', 'cpf')
    list_filter = ('departamento', 'desligado')
    inlines = [DependenteInline, LancamentoInline] # Permite editar dependentes e folha dentro do cadastro

@admin.register(EventoFolha)
class EventoFolhaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'tipo', 'incide_inss')
    ordering = ('codigo',)

@admin.register(LancamentoMensal)
class LancamentoMensalAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'evento', 'mes_referencia', 'valor')
    list_filter = ('mes_referencia', 'evento')

@admin.register(RegistroPonto)
class PontoAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'data', 'entrada_1', 'saida_2', 'horas_extras')
    list_filter = ('data', 'funcionario')

admin.site.register(HistoricoCargoSalario)
admin.site.register(ControleFerias)