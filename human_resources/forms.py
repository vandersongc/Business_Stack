from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_desligamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'desligado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'onclick': 'toggleDesligamento()'}),
            # Estilização inputs numéricos
            'salario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_vale_transporte': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_vale_alimentacao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_assist_medica': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'desc_assist_odonto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }