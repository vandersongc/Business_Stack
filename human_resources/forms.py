from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = ['nome', 'cargo', 'departamento', 'data_admissao', 'salario', 
                  'cep', 'logradouro', 'numero', 'bairro', 'cidade', 'uf']
        
        # Adiciona classes CSS e placeholders para ficar bonito
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'onblur': 'buscarCep()'}), # Opcional se usar o script separado
            'logradouro': forms.TextInput(attrs={'class': 'form-control'}),
            # ... adicione classes aos outros campos se desejar manter o padrão visual
        }