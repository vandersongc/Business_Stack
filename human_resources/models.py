from django.db import models
from decimal import Decimal

class Funcionario(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'), ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'), ('viuvo', 'Viúvo(a)'),
    ]
    TIPO_CONTRATO_CHOICES = [('clt', 'CLT'), ('pj', 'PJ'), ('estagio', 'Estágio')]
    # (Mantenha seus choices de DEPARTAMENTOS e UF aqui para economizar espaço...)
    DEPARTAMENTOS_CHOICES = [
        ('TI', 'Tecnologia da Informação'), ('RH', 'Recursos Humanos'), ('FIN', 'Financeiro'),
        ('ADM', 'Administrativo'), ('COM', 'Comercial'), ('LOG', 'Logística'),
        ('JUR', 'Jurídico'), ('MKT', 'Marketing')
    ]
    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'),
        ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
        ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
        ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ]

    # --- DADOS PESSOAIS ---
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    email = models.EmailField(verbose_name="E-mail Pessoal", blank=True, null=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, verbose_name="Estado Civil", blank=True, null=True)

    # --- DADOS CONTRATUAIS ---
    cargo = models.CharField(max_length=100, verbose_name="Cargo")
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    lotacao = models.CharField(max_length=100, verbose_name="Lotação", blank=True, null=True)
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário Base")
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='clt')

    # --- DADOS BANCÁRIOS ---
    banco = models.CharField(max_length=50, verbose_name="Banco", blank=True, null=True)
    agencia = models.CharField(max_length=10, verbose_name="Agência", blank=True, null=True)
    conta = models.CharField(max_length=20, verbose_name="Conta", blank=True, null=True)

    # --- DESCONTOS FIXOS (Conforme seu PDF) ---
    desc_vale_transporte = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Vale Transporte")
    desc_vale_alimentacao = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Vale Alimentação")
    desc_assist_medica = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Assist. Médica")
    desc_assist_odonto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Assist. Odonto")

    # --- ENDEREÇO ---
    cep = models.CharField(max_length=10, verbose_name="CEP", blank=True, null=True)
    logradouro = models.CharField(max_length=200, verbose_name="Endereço", blank=True, null=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", blank=True, null=True)
    uf = models.CharField(max_length=2, verbose_name="UF", blank=True, null=True)

    # --- STATUS ---
    desligado = models.BooleanField(default=False, verbose_name="Colaborador Desligado?")
    data_desligamento = models.DateField(verbose_name="Data do Desligamento", blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome_completo

    # === CÁLCULOS LEGAIS VIGENTES (2024/2025) ===
    def calcular_inss(self):
        salario = self.salario or Decimal(0)
        teto = Decimal('7786.02')
        if salario > teto: return Decimal('908.85')

        desc = Decimal(0)
        # Faixas Progressivas
        faixas = [
            (Decimal('1412.00'), Decimal('0.075')),
            (Decimal('2666.68'), Decimal('0.09')),
            (Decimal('4000.03'), Decimal('0.12')),
            (teto, Decimal('0.14'))
        ]
        
        base_anterior = Decimal(0)
        for limite, aliquota in faixas:
            if salario > base_anterior:
                base_faixa = min(salario, limite) - base_anterior
                desc += base_faixa * aliquota
                base_anterior = limite
            else:
                break
        return desc

    def calcular_irpf(self):
        base = (self.salario or Decimal(0)) - self.calcular_inss()
        # Tabela Progressiva Mensal
        if base <= Decimal('2259.20'): return Decimal(0)
        elif base <= Decimal('2826.65'): return (base * Decimal('0.075')) - Decimal('169.44')
        elif base <= Decimal('3751.05'): return (base * Decimal('0.15')) - Decimal('381.44')
        elif base <= Decimal('4664.68'): return (base * Decimal('0.225')) - Decimal('662.77')
        else: return (base * Decimal('0.275')) - Decimal('896.00')

    @property
    def total_descontos(self):
        impostos = self.calcular_inss() + self.calcular_irpf()
        fixos = self.desc_vale_transporte + self.desc_vale_alimentacao + self.desc_assist_medica + self.desc_assist_odonto
        return impostos + fixos

    @property
    def salario_liquido(self):
        return (self.salario or Decimal(0)) - self.total_descontos

    @property
    def fgts_mes(self):
        return (self.salario or Decimal(0)) * Decimal('0.08')