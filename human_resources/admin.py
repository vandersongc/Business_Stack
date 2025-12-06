from django.contrib import admin
from .models import Funcionario

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    # Colunas que aparecem na lista
    list_display = ('nome_completo', 'departamento', 'cargo', 'email', 'telefone', 'data_admissao')
    
    # Filtros laterais
    list_filter = ('departamento', 'tipo_contrato', 'estado_civil', 'uf')
    
    # Barra de pesquisa (busca por nome ou CPF)
    search_fields = ('nome_completo', 'cpf', 'email')
    
    # Organização do formulário dentro do Admin
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'data_nascimento', 'email', 'telefone', 'estado_civil')
        }),
        ('Dados Contratuais', {
            'fields': ('cargo', 'departamento', 'data_admissao', 'salario', 'tipo_contrato')
        }),
        ('Endereço', {
            'fields': ('cep', 'logradouro', 'numero', 'bairro', 'cidade', 'uf')
        }),
    )