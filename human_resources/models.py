from django.db import models
from decimal import Decimal

class Funcionario(models.Model):
    # --- Opções de escolha (Dropdowns) ---

    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
    ]

    TIPO_CONTRATO_CHOICES = [
        ('clt', 'CLT'),
        ('pj', 'PJ'),
        ('estagio', 'Estágio'),
    ]

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

    # --- Dados Pessoais ---
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    email = models.EmailField(verbose_name="E-mail Pessoal", blank=True, null=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil", blank=True, null=True)

    # --- Dados Contratuais ---
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário", blank=True, null=True)
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, verbose_name="Tipo de Contrato", default='clt')

    # --- Endereço ---
    cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    logradouro = models.CharField(max_length=200, verbose_name="Endereço", blank=True, null=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    uf = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)

    # Registro de sistema
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_completo
    
    # --- CAMPOS PARA DESLIGAMENTO ---
    desligado = models.BooleanField(default=False, verbose_name="Colaborador Desligado?")
    data_desligamento = models.DateField(verbose_name="Data do Desligamento", blank=True, null=True)

    # ... (restante dos campos: cep, logradouro, criado_em, def __str__) ...

    # --- CÁLCULOS AUTOMÁTICOS (PROPRIEDADES) ---
    @property
    def calculo_descontos(self):
        """Simulação de descontos (ex: 11% de INSS + 6% VT = 17% fixo para exemplo)"""
        if self.salario:
            return self.salario * Decimal('0.17')
        return Decimal('0.00')

    @property
    def salario_liquido(self):
        """Salário Bruto - Descontos"""
        if self.salario:
            return self.salario - self.calculo_descontos
        return Decimal('0.00')