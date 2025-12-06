from django.db import models

class Funcionario(models.Model):
    # --- Opções de escolha (Dropdowns) ---
    DEPARTAMENTOS_CHOICES = [
        ('TI', 'Tecnologia da Informação'),
        ('RH', 'Recursos Humanos'),
        ('FIN', 'Financeiro'),
        ('ADM', 'Administrativo'),
        ('COM', 'Comercial'),
        ('LOG', 'Logística'),
        ('JUR', 'Jurídico'),
        ('MKT', 'Marketing'),
    ]

    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
        ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
        ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'),
        ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]

    # --- Dados Pessoais e Profissionais ---
    nome = models.CharField(max_length=100, verbose_name="Nome Completo")
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    
    # Aqui usamos o choices para criar o Dropdown no formulário
    departamento = models.CharField(
        max_length=3, 
        choices=DEPARTAMENTOS_CHOICES, 
        default='RH',
        verbose_name="Departamento"
    )
    
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário")

    # --- Endereço (Integração com ViaCEP) ---
    cep = models.CharField(max_length=9, verbose_name="CEP")
    logradouro = models.CharField(max_length=100, verbose_name="Endereço", blank=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True)
    bairro = models.CharField(max_length=50, verbose_name="Bairro", blank=True)
    cidade = models.CharField(max_length=50, verbose_name="Cidade", blank=True)
    
    # Dropdown também para o Estado (UF)
    uf = models.CharField(
        max_length=2, 
        choices=UF_CHOICES, 
        verbose_name="Estado", 
        blank=True
    )

    # Registro de sistema
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome