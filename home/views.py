from django.shortcuts import render
from django.http import HttpResponse

# Crie a função 'home' que o seu urls.py está procurando
def home(request):
    return render(request, 'home.html') 