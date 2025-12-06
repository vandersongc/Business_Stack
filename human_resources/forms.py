from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
        widgets = {
            # --- Campos de Data ---
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_desligamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # --- Campos Checkbox ---
            'desligado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'onclick': 'toggleDesligamento()'}),
            
            # --- Campos Numéricos e Monetários ---
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_vale_transporte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_vale_alimentacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_assist_medica': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_assist_odonto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            
            # --- Campos de Texto e Endereço (Atualizados) ---
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '14'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'lotacao': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'conta': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Endereço
            'cep': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '9', 'id': 'id_cep'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_logradouro'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_numero'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_complemento'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cidade'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_uf'}),
            
            # Selects
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
        }