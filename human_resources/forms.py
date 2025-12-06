from django import forms
from .models import Funcionario

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        # O atalho '__all__' pega todos os campos do modelo automaticamente
        fields = '__all__'