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
    
    # --- Status ---
    desligado = models.BooleanField(default=False, verbose_name="Colaborador Desligado?")
    data_desligamento = models.DateField(verbose_name="Data do Desligamento", blank=True, null=True)

    # Registro de sistema
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_completo

    # =================================================================
    # === CÁLCULOS DE FOLHA DE PAGAMENTO (LEGISLAÇÃO VIGENTE) ===
    # =================================================================

    def calcular_inss(self):
        """Calcula o INSS Progressivo (Tabela 2024/2025)"""
        salario = self.salario or Decimal(0)
        teto_inss = Decimal('7786.02')
        
        if salario > teto_inss:
            return Decimal('908.85')

        desconto = Decimal(0)
        faixa1 = Decimal('1412.00')
        faixa2 = Decimal('2666.68')
        faixa3 = Decimal('4000.03')

        if salario > faixa1:
            desconto += faixa1 * Decimal('0.075')
        else:
            return salario * Decimal('0.075')

        if salario > faixa2:
            desconto += (faixa2 - faixa1) * Decimal('0.09')
        else:
            return desconto + (salario - faixa1) * Decimal('0.09')

        if salario > faixa3:
            desconto += (faixa3 - faixa2) * Decimal('0.12')
        else:
            return desconto + (salario - faixa2) * Decimal('0.12')

        return desconto + (salario - faixa3) * Decimal('0.14')

    def calcular_irpf(self):
        """Calcula o Imposto de Renda (Base - INSS)"""
        salario = self.salario or Decimal(0)
        inss = self.calcular_inss()
        base_calculo = salario - inss
        
        if base_calculo <= Decimal('2259.20'):
            return Decimal(0)
        elif base_calculo <= Decimal('2826.65'):
            return (base_calculo * Decimal('0.075')) - Decimal('169.44')
        elif base_calculo <= Decimal('3751.05'):
            return (base_calculo * Decimal('0.15')) - Decimal('381.44')
        elif base_calculo <= Decimal('4664.68'):
            return (base_calculo * Decimal('0.225')) - Decimal('662.77')
        else:
            return (base_calculo * Decimal('0.275')) - Decimal('896.00')

    @property
    def calculo_descontos(self):
        """Total de descontos (INSS + IRPF)"""
        return self.calcular_inss() + self.calcular_irpf()
    
    # Alias para manter compatibilidade com códigos anteriores que usam total_descontos
    @property
    def total_descontos(self):
        return self.calculo_descontos

    @property
    def salario_liquido(self):
        """Salário Bruto - Total de Descontos"""
        return (self.salario or Decimal(0)) - self.calculo_descontos