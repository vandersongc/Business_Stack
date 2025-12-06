from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        # O atalho '__all__' pega todos os campos do modelo automaticamente
        fields = '__all__'
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_desligamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), # Novo
            'desligado': forms.CheckboxInput(attrs={'class': 'form-check-input', 'onclick': 'toggleDesligamento()'}), # Novo com gatilho JS
            # ... outros widgets ...
        }