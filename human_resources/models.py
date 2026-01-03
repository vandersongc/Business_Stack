import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.db import models
from decimal import Decimal
from django.utils import timezone


class Funcionario(models.Model):
    # --- CHOICES ---
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'), ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'), ('viuvo', 'Viúvo(a)'),
    ]
    TIPO_CONTRATO_CHOICES = [('clt', 'CLT'), ('pj', 'PJ'), ('estagio', 'Estágio')]
    
    DEPARTAMENTOS_CHOICES = [
        ('TI', 'Tecnologia da Informação'), ('RH', 'Recursos Humanos'), ('FIN', 'Financeiro'),
        ('ADM', 'Administrativo'), ('COM', 'Comercial'), ('LOG', 'Logística'),
        ('JUR', 'Jurídico'), ('MKT', 'Marketing')
    ]
    
    # --- DADOS PESSOAIS ---
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True)
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    email = models.EmailField(verbose_name="E-mail Pessoal", blank=True, null=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone", blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)

    # --- DADOS CONTRATUAIS ---
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    lotacao = models.CharField(max_length=100, blank=True, null=True)
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    salario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Salário Base Atual")
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='clt')

    # --- ENDEREÇO & BANCO ---
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    
    banco = models.CharField(max_length=50, blank=True, null=True)
    agencia = models.CharField(max_length=10, blank=True, null=True)
    conta = models.CharField(max_length=20, blank=True, null=True)

    # --- CAMPOS LEGADOS ---
    desc_vale_transporte = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Vale Transporte (Fixo)")
    desc_vale_alimentacao = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Vale Alimentação (Fixo)")
    desc_assist_medica = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Assist. Médica (Fixo)")
    desc_assist_odonto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desc. Assist. Odonto (Fixo)")

    # --- STATUS ---
    desligado = models.BooleanField(default=False)
    data_desligamento = models.DateField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    foto = models.ImageField(upload_to='funcionarios/fotos/', blank=True, null=True, verbose_name="Foto 3x4")
    qr_code_img = models.ImageField(upload_to='funcionarios/qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.nome_completo

    def save(self, *args, **kwargs):
        # 1. Salva primeiro os dados normais para garantir que temos o ID
        super().save(*args, **kwargs)

        # 2. Se o QR Code ainda não existe, cria agora (que já temos ID)
        if not self.qr_code_img:
            # Gera a imagem do QR Code
            qrcode_img = qrcode.make(f"FUNC-{self.id}")
            
            # Redimensiona para garantir compatibilidade com o canvas
            qrcode_img = qrcode_img.resize((290, 290))
            
            # Cria um canvas branco
            canvas = Image.new('RGB', (290, 290), 'white')
            
            # Cola o QR Code na posição (0,0) -> CORREÇÃO DO ERRO
            canvas.paste(qrcode_img, (0, 0))
            
            # Salva em memória
            fname = f'qr_code-{self.nome_completo}.png'
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            
            # Atribui ao campo do modelo (save=False para não salvar no banco ainda)
            self.qr_code_img.save(fname, File(buffer), save=False)
            
            # Salva novamente APENAS o campo do QR Code para evitar recursão infinita
            super().save(update_fields=['qr_code_img'])

# === MÓDULO 1: ADMINISTRAÇÃO DE PESSOAL (Novos) ===

class Dependente(models.Model):
    TIPO_CHOICES = [('filho', 'Filho(a)'), ('conjuge', 'Cônjuge'), ('pais', 'Pais')]
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='dependentes')
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14, blank=True, null=True)
    irrf = models.BooleanField(default=True, verbose_name="Abate no IRRF?")
    salario_familia = models.BooleanField(default=True, verbose_name="Recebe Sal. Família?")

    def __str__(self):
        return f"{self.nome} ({self.funcionario.nome_completo})"

class HistoricoCargoSalario(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    data_alteracao = models.DateField()
    cargo_anterior = models.CharField(max_length=100)
    cargo_novo = models.CharField(max_length=100)
    salario_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    salario_novo = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.funcionario} - {self.data_alteracao}"

# === MÓDULO 2: FOLHA DE PAGAMENTO (Dinâmica) ===

class EventoFolha(models.Model):
    TIPO_CHOICES = [('V', 'Vencimento'), ('D', 'Desconto')]
    codigo = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    incide_inss = models.BooleanField(default=True)
    incide_irrf = models.BooleanField(default=True)
    incide_fgts = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class LancamentoMensal(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='lancamentos')
    evento = models.ForeignKey(EventoFolha, on_delete=models.PROTECT)
    mes_referencia = models.CharField(max_length=7)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = "Lançamento Mensal"
        verbose_name_plural = "Lançamentos Mensais"
    
    def __str__(self):
        return f"{self.funcionario} - {self.evento} - {self.valor}"

# === MÓDULO 3: PONTO E FREQUÊNCIA ===

class RegistroPonto(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    data = models.DateField()
    entrada_1 = models.TimeField(blank=True, null=True)
    saida_1 = models.TimeField(blank=True, null=True)
    entrada_2 = models.TimeField(blank=True, null=True)
    saida_2 = models.TimeField(blank=True, null=True)
    horas_extras = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    atrasos = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    observacao = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Ponto {self.funcionario} - {self.data}"

# === MÓDULO 4: FÉRIAS ===

class ControleFerias(models.Model):
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    periodo_aquisitivo_inicio = models.DateField()
    periodo_aquisitivo_fim = models.DateField()
    dias_direito = models.IntegerField(default=30)
    dias_gozados = models.IntegerField(default=0)
    saldo_dias = models.IntegerField(default=30)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"Férias {self.funcionario} ({self.periodo_aquisitivo_inicio})"