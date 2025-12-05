from django.shortcuts import render

# Página Inicial
def home(request):
    return render(request, 'home.html') 

# Cadastro
def cadastro(request):
    return render(request, 'cadastro.html')

# Login
def login(request):
    return render(request, 'login.html')