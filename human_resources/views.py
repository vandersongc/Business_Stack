from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Adicione @login_required se quiser proteger a página
@login_required
def home_rh(request):
    return render(request, 'home_rh.html')