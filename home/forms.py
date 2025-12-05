from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CadastroForm(UserCreationForm):
    # Adicionando o campo de e-mail obrigatório
    email = forms.EmailField(required=True, label="E-mail")

    class Meta:
        model = User
        # Define a ordem: Usuário, E-mail, Senhas
        fields = ("username", "email")