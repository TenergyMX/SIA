from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import *
from datetime import datetime, timedelta
from django.contrib.postgres.fields import ArrayField
import re

# Create your models here.
class Vehicle(models.Model):
    is_active = models.BooleanField(default=True)
    image_path = models.FileField(upload_to='docs/', blank=True, null=True)                 # Imagen del vehiculo
    name = models.CharField(max_length=64, blank=True, null=True)                           # Nombre del vehiculo
    state = models.CharField(max_length=64, blank=True, null=True)                          # Estado del vehiculo
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)   # Empresa
    plate = models.CharField(max_length=10)                                                 # Placa
    model = models.CharField(max_length=100, blank=True, null=True)                         # Modelo
    year = models.IntegerField(blank=True, null=True, default=None)                         # año
    serial_number = models.CharField(max_length=100, blank=True, null=True)                 # Numero de serie
    brand = models.CharField(max_length=100, blank=True, null=True)                         # Marca
    color = models.CharField(max_length=50, blank=True, null=True)                          # Color
    vehicle_type = models.CharField(max_length=32, blank=True, null=True)                   # Tipo de vehiculo
    validity = models.DateField(blank=True, null=True, verbose_name="Vigencia")             # Vigencia
    policy_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de póliza") # Número de polisa
    mileage = models.IntegerField(blank=True, default=0)   # Kilometraje
    insurance_company = models.CharField(max_length=100, blank=True, null=True)             # Aseguradora
    qr_info = models.FileField(upload_to='qrcodes/info/', blank=True, null=True)
    qr_access = models.FileField(upload_to='qrcodes/access/', blank=True, null=True)
    email_sin_tenencia = models.BooleanField(default=False)
    email_sin_refrendo = models.BooleanField(default=False)
    email_sin_verificacion = models.BooleanField(default=False)
    email_sin_responsive = models.BooleanField(default=False)
    email_sin_insurance = models.BooleanField(default=False)
    email_sin_audit = models.BooleanField(default=False)
    email_sin_maintenance = models.BooleanField(default=False)
    email_verificacion_s1 = models.BooleanField(default=False) 
    email_verificacion_s2 = models.BooleanField(default=False)
    qr_fuel = models.FileField(upload_to='qrcodes/access/', blank=True, null=True)
    fuel_type_vehicle = models.TextField(blank=True, null=True, verbose_name="Tipo de Combustible")
    apply_tenencia = models.BooleanField(default=False, verbose_name="Aplica tenencia") 

    responsible = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name="Responsable",
        related_name="responsible_for_the_vehicle",
    )
    transmission_type = models.CharField(
        max_length=32, blank=True,
        null=True, default='Automatico',
        verbose_name="Tipo de transmisión",
        help_text="Estándar o Automático"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True, null=True,
        verbose_name="Propietario",
        related_name="vehicle_owner"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        owner_name = self.owner.username if self.owner else "Sin propietario"
        return f"{self.brand} {self.model} ({self.plate}) - {owner_name}"

class Vehicle_Maintenance_Kilometer(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    kilometer = models.IntegerField(default=0, blank=True)
    status = models.CharField(max_length=50, null=True, default="current")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehiculo} - Mantenimiento en {self.kilometer} Km"

class Vehicle_Tenencia(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_pago = models.DateField()
    comprobante_pago = models.FileField(upload_to='docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_tenencia = models.BooleanField(default=False)

    def clean(self):
        # Validar que el monto de la tenencia sea positivo
        if self.monto is not None and self.monto <= 0:
            raise ValidationError("El monto de la tenencia debe ser mayor que cero")

    def __str__(self):
        return f'Tenencia de {self.vehiculo} - Pagado el {self.fecha_pago}'

class Vehicle_Refrendo(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_pago = models.DateField()
    comprobante_pago = models.FileField(upload_to='docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_refrendo = models.BooleanField(default=False)

    def __str__(self):
        return f"Refrendo vehicular para {self.vehiculo}"
    
class Vehicle_Verificacion(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    engomado = models.CharField(max_length=50, blank=True, null=True)
    periodo = models.CharField(max_length=50, blank=True, null=True)
    fecha_pago = models.DateField()
    lugar = models.CharField(max_length=100, blank=True, null=True)
    comprobante_pago = models.FileField(upload_to='docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email_verificacion = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('PENDIENTE','Pendiente'),
        ('PAGADO','Pagado'),
        ('PROXIMO','Próximo'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f"Verificación vehicular para {self.vehiculo}"
    
class Vehicle_Responsive(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    image_path_entry_1 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_entry_2 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_exit_1 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_exit_2 = models.FileField(upload_to='docs/', blank=True, null=True)
    initial_mileage = models.IntegerField(blank=True, default=0)   # Kilometraje
    final_mileage = models.IntegerField(blank=True, default=0)   # Kilometraje
    initial_fuel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_fuel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    signature = models.FileField(upload_to='docs/', blank=True, null=True)  # imagen de la firma
    destination = models.CharField(max_length=255, blank=True, null=True)   # Destino
    trip_purpose = models.CharField(max_length=255, blank=True, null=True)  # Proposito del viaje
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Responsiva para {self.vehicle}"    
    
    class Meta:
        verbose_name = "Responsiva de Vehículo"
        verbose_name_plural = "Responsivas de Vehículos"

class Vehicle_Insurance(models.Model):
    """
    Modelo optimizado para seguros vehiculares con nuevos estados
    """
    ESTADOS = (
        ('PAGADO', 'PAGADO'),
        ('PROXIMO', 'PROXIMO'),
        ('VENCIDO', 'VENCIDO'),
        ('PENDIENTE', 'PENDIENTE'),
        ('HISTORICO', 'HISTORICO')
    )
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    policy_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de póliza")
    insurance_company = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    validity = models.IntegerField()    # Vigencia
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    doc = models.FileField(upload_to='docs/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    email_insurance = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ESTADOS, default='PROXIMO')
    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
            models.Index(fields=['vehicle', 'policy_number']),
        ]

class Vehicle_Audit(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    audit_date = models.DateField()
    general_notes = models.TextField(blank=True, null=True)
    checks = models.TextField(blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email_audit = models.BooleanField(default=False)

    def __str__(self):
        return f"Auditoría de {self.vehicle} el {self.audit_date}"


class Vehicle_Maintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mileage = models.IntegerField(blank=True, default=0)   # Kilometraje
    time = models.CharField(max_length=100, blank=True, null=True, help_text="Tiempo")
    general_notes = models.TextField(max_length=255, blank=True, null=True)
    actions = models.TextField(blank=True, null=True)
    comprobante = models.FileField(upload_to='docs/', blank=True, null=True, help_text="Comprobante de pago o de matenimiento")
    is_checked = models.BooleanField(default=False)
    status = models.CharField(max_length=255, null=False, default="blank")
    created_at = models.DateTimeField(auto_now_add=True)
    email_maintenance = models.BooleanField(default=False)
    email_maintenance_proximo = models.BooleanField(default=False)
    email_maintenance_recordatorio = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.vehicle} - {self.type} - {self.date}"
    
    class Meta:
        verbose_name = 'Mantenimiento de Vehículo'
        verbose_name_plural = 'Mantenimiento de Vehículos'

class Vehicle_Driver(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="compañía")
    name_driver = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nombre del conductor" ,blank=True, null=True)
    image_path = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="Responsable del equipo")                 # fotografia del conductor 
    number_phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de telefono")                
    address = models.TextField(max_length=80, blank=True, null=True, verbose_name="Dirección")

class Licences_Driver(models.Model):
    name_driver = models.ForeignKey(Vehicle_Driver, on_delete=models.CASCADE, verbose_name="Nombre del conductor" ,blank=True, null=True)
    start_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    expiration_date = models.DateField(blank=True, null=True, verbose_name="Fecha de expiración de licencia")
    #license_driver = models.ForeignKey(Vehicle_Driver, on_delete=models.CASCADE, blank=True, null=True, verbose_name="licencia de conducir")
    license_driver = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="licencia de conducir")

class Multas(models.Model):
    name_driver = models.ForeignKey(Vehicle_Driver, on_delete=models.CASCADE, verbose_name="Nombre del conductor" ,blank=True, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Vehiculo")
    cost = models.DecimalField(max_digits=50, decimal_places=2, blank=True, null=True, verbose_name='Costo')
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    reason = models.TextField(blank=True, null=True, verbose_name="Razón")
    date = models.DateField(blank=True, null=True, verbose_name="Fecha")

class Checks(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)

class Placas(models.Model):
    plate = models.CharField(max_length=255)                                               
    type_plate = models.CharField(max_length=64, blank=True, null=True)                        
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    entidad_emisora= models.CharField(max_length=64, blank=True, null=True)                        
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    status = models.CharField(max_length=255, null=False, default="blank")
    document_placa = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de placa")

class Letter_Facturas_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    document_letter_factura = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de factura")

class Facturas_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    name_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nombre del conductor" ,blank=True, null=True)
    fecha_vencimiento = models.DateField()
    number = models.CharField(max_length=255)                                               
    status = models.CharField(max_length=255, null=False, default="blank")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    document_factura = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de factura")

class Card_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    number_card = models.CharField(max_length=50)      
    type_card = models.CharField(max_length=64, blank=True, null=True)   
    name_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nombre del conductor" ,blank=True, null=True)                                                      
    status = models.CharField(max_length=255, null=False, default="blank")
    document_card = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de tarjeta") 
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name="Fecha")

class Contract_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    type_contract = models.CharField(max_length=64, blank=True, null=True)  
    fecha_contract = models.DateField()
    fecha_finiquito = models.DateField()
    status_modified = models.BooleanField(default=False, verbose_name="Estado modificado")  
    document_contract = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de contrato") 
    document_letter = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="carta de finiquito") 
    is_canceled = models.BooleanField(default=False, verbose_name="Contrato cancelado")  # nuevo campo

class Hologram_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    date_hologram = models.DateField()
    document_hologram = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de holograma")

class Carnet_Vehicle(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    date_carnet = models.DateField()
    document_carnet = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="documento de carnet")







# Todo ----- [2] [ EQUIPOS DE COMPUTO ] -----
class ComputerSystem(models.Model):
    is_active = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    serial_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de Serie")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre")
    equipment_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tipo de Equipo")
    so = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sistema Operativo")
    brand = models.CharField(max_length=50, blank=True, null=True, verbose_name="Marca")
    model = models.CharField(max_length=50, blank=True, null=True, verbose_name="Modelo")
    processor = models.CharField(max_length=50, blank=True, null=True, verbose_name="Procesador")
    num_cores = models.IntegerField(blank=True, null=True, verbose_name="Número de Núcleos")
    processor_speed = models.FloatField(blank=True, null=True, verbose_name="Velocidad del Procesador")
    architecture = models.CharField(max_length=20, blank=True, null=True, verbose_name="Arquitectura del Procesador")
    disk_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Disco Duro")
    disk_capacity = models.CharField(max_length=20, blank=True, null=True, verbose_name="Capacidad de Almacenamiento")
    ram = models.IntegerField(blank=True, null=True, verbose_name="RAM")
    ram_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tipo de RAM")
    ram_speed = models.IntegerField(blank=True, null=True, verbose_name="Velocidad de RAM")
    graphics_card = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tarjeta Gráfica")
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name="Color")
    battery = models.CharField(max_length=50, blank=True, null=True, verbose_name="Batería")
    warranty = models.CharField(max_length=50, blank=True, null=True, verbose_name="Garantía")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación")
    previous_responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='previous_responsible', verbose_name="Responsable Anterior")
    current_responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='current_responsible', verbose_name="Responsable Actual")
    equipment_status = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estado del Equipo")
    last_maintenance_date = models.DateField(blank=True, null=True, verbose_name="Fecha del Último Mantenimiento")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    qr_info_computer = models.FileField(upload_to='qrcodes/info/', blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="Identificador")
    adquisition_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Adquisición")

    class Meta:
        verbose_name = "Equipo de Computo"
        verbose_name_plural = "Equipos de Computo"

    def generar_identificador(self):
        if self.equipment_type and self.company:
            prefix_map = {
                "portátil": "LAP",
                "sobremesa": "COMP",
                "servidor": "SERV"
            }

            # Obtener las 3 primeras letras del tipo de equipo
            prefix = prefix_map.get(self.equipment_type.lower(), "EQP")

            # Obtener las 3 primeras letras de la empresa, asegurando que no sea más largo de 3 caracteres
            company_name = self.company.name if self.company and self.company.name else ""
            company_initials = company_name[:3].upper()  # Las 3 primeras letras de la empresa

            # Combinar el prefijo y las iniciales de la empresa
            base_identifier = f"{prefix}-{company_initials}"

            # Filtrar para obtener el último identificador de la misma empresa, que es el último con el mismo prefijo
            last_identifier = ComputerSystem.objects.filter(
                company=self.company
            ).values_list("identifier", flat=True)
            
            last_id_number = 0
            for ident in last_identifier:
                match = re.search(r'(\d+)$', ident)
                if match:
                    last_id_number = max(last_id_number, int(match.group(1)))

            # Generar el siguiente número consecutivo
            next_id_number = last_id_number + 1

            # Generar el identificador final con 4 dígitos
            return f"{base_identifier}-{next_id_number:04d}"

        return None

    def save(self, *args, **kwargs):
        # Generar identificador si no existe
        if not self.identifier:
            self.identifier = self.generar_identificador()
        
        # Guardar el registro actual
        super().save(*args, **kwargs)

        # Verificar y actualizar los registros existentes sin identificador
        equipos_sin_identificador = ComputerSystem.objects.filter(identifier__isnull=True)
        for equipo in equipos_sin_identificador:
            equipo.identifier = equipo.generar_identificador()
            equipo.save()

    def __str__(self):
        return f"{self.identifier} - {self.name} ({self.brand} {self.model})"


class ComputerPeripheral(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre")
    peripheral_type = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tipo de Periférico")
    brand = models.CharField(max_length=50, blank=True, null=True, verbose_name="Marca")
    model = models.CharField(max_length=50, blank=True, null=True, verbose_name="Modelo")
    serial_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número de Serie")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    acquisition_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Adquisición")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ubicación")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Responsable")
    peripheral_status = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estado del Periférico")
    comments = models.TextField(blank=True, null=True, verbose_name="Comentarios")
    identifier = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="Identificador")

    class Meta:
        verbose_name = "Periférico de Equipo de Computo"
        verbose_name_plural = "Periféricos de Equipos de Computo"

    def generar_identificador(self):
        if self.peripheral_type and self.company:
            # Obtener las primeras 3 letras del tipo de periférico
            peripheral_type_prefix = self.peripheral_type[:3].upper()

            # Obtener las primeras 3 letras del nombre de la empresa
            company_name_prefix = self.company.name[:3].upper()

            # Crear el prefijo con el tipo de periférico y el nombre de la empresa
            base_identifier = f"{peripheral_type_prefix}-{company_name_prefix}"

            # Filtrar registros solo de la misma compañía y con el mismo prefijo
            existing_identifiers = ComputerPeripheral.objects.filter(
                company=self.company,  # Filtra por la misma empresa
                identifier__startswith=base_identifier  # Filtra por el prefijo del identificador
            ).values_list('identifier', flat=True)

            # Extraer el número más alto generado para este tipo y compañía
            last_id_number = 0
            for ident in existing_identifiers:
                match = re.search(r'(\d+)$', ident)
                if match:
                    last_id_number = max(last_id_number, int(match.group(1)))

            # Generar el siguiente número consecutivo
            next_id_number = last_id_number + 1

            # Generar el identificador final con 4 dígitos
            return f"{base_identifier}-{next_id_number:04d}"

        return None  # Se agrega para manejar casos donde no se cumple la condición

    def save(self, *args, **kwargs):
        # Generar identificador si no existe
        if not self.identifier:
            self.identifier = self.generar_identificador()

        # Guardar el registro actual
        super().save(*args, **kwargs)

        # Verificar y actualizar los registros existentes sin identificador
        equipos_sin_identificador = ComputerPeripheral.objects.filter(identifier__isnull=True)
        for equipo in equipos_sin_identificador:
            equipo.identifier = equipo.generar_identificador()
            equipo.save()

    def __str__(self):
        return f"{self.identifier} - {self.name} ({self.brand} {self.model})"


class Software(models.Model):
    SOFTWARE_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('package', 'Paquete'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    function = models.CharField(max_length=34, blank=True, null=True, verbose_name="Función del Software", help_text="Por ejemplo: Antivirus, Editor de texto, Suite de oficina, etc.")
    name = models.CharField(max_length=100, verbose_name="Nombre del Software")
    version = models.CharField(max_length=50, blank=True, null=True, verbose_name="Versión del Software")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción del Software")
    software_type = models.CharField(max_length=10, choices=SOFTWARE_TYPE_CHOICES, default='individual', verbose_name="Tipo de Software")
    is_unlimited = models.BooleanField(default=False, verbose_name="Instalaciones Ilimitadas")
    max_installations = models.IntegerField(blank=True, null=True, verbose_name="Máximo de Instalaciones")
    installation_count = models.IntegerField(default=0, verbose_name="Contador de Instalaciones")

    class Meta:
        verbose_name = "Software"
        verbose_name_plural = "Softwares"

    def __str__(self):
        return self.name
    
class SoftwareInstallation(models.Model):
    software = models.ForeignKey('Software', on_delete=models.CASCADE, verbose_name="Software", blank=True, null=True)
    software_identifier = models.CharField(max_length=255, verbose_name="Identificador del Software", help_text="Identificador del software proporcionado por el proveedor")
    computerSystem = models.ForeignKey('ComputerSystem', on_delete=models.CASCADE, verbose_name="Equipo")
    installation_date = models.DateField(auto_now_add=True, verbose_name="Fecha de Instalación")

    class Meta:
        verbose_name = "Instalación de Software"
        verbose_name_plural = "Instalaciones de Software"

    def __str__(self):
        return f"{self.software.name if self.software else 'Software sin nombre'} en {self.computerSystem.name}"
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.software:
            raise ValidationError("Debe especificar un software.")
        
    def save(self, *args, **kwargs):
        # Actualizar el contador de instalaciones del software al guardar la instalación
        self.software.installation_count = SoftwareInstallation.objects.filter(software=self.software).count()
        self.software.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Actualizar el contador de instalaciones del software al eliminar la instalación
        self.software.installation_count = SoftwareInstallation.objects.filter(software=self.software).count() - 1
        self.software.save()
        super().delete(*args, **kwargs)
        

class ComputerEquipment_Maintenance(models.Model):
    computerSystem = models.ForeignKey(
        'ComputerSystem',
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name="Equipo"
    )
    performed_by = models.CharField(max_length=100, blank=True,null=True, verbose_name='¿Quién lo hizo?', help_text="Usuario o Proveedor")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Proveedor")
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Usuario")
    type = models.CharField(max_length=100,blank=True, null=True, verbose_name='Tipo de mantenimiento')
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Costo')
    actions = models.TextField( blank=True,null=True,verbose_name='Acciones')
    document = models.FileField(upload_to='doc/maintenance/', blank=True, null=True, verbose_name='Documento')
    is_checked = models.BooleanField(default=False)
    date = models.DateField(blank=True, null=True, verbose_name='Fecha de mantenimiento')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mantenimiento de Equipo de Computo'
        verbose_name_plural = 'Mantenimiento de Equipos de Computo'

    def __str__(self):
        return f"{self.type if self.type else 'Sin tipo'}"

class ComputerEquipment_Audit(models.Model):
    computerSystem = models.ForeignKey(
        'ComputerSystem',
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name="Equipo"
    )
    audit_date = models.DateField(blank=True, null=True, verbose_name="Fecha de la Auditoria")

    pantalla_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estatus de la Pantalla")
    pantalla_notas = models.TextField(blank=True, null=True, verbose_name="Notas del Estatus de la Pantalla")

    teclado_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estatus del Teclado")
    teclado_notas = models.TextField(blank=True, null=True, verbose_name="Notas del Estatus del Teclado")

    puertos_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estatus de los Puertos")
    puertos_notas = models.TextField(blank=True, null=True, verbose_name="Notas del Estatus de los Puertos")

    cargador_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estatus del Cargador")
    cargador_notas = models.TextField(blank=True, null=True, verbose_name="Notas del Estatus del Cargador")

    carcasa_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estatus de la Carcasa del Equipo")
    carcasa_notas = models.TextField(blank=True, null=True, verbose_name="Notas del Estatus de la Carcasa del Equipo")

    limpieza_check = models.CharField(max_length=20, blank=True, null=True, verbose_name="Limpieza del Equipo")
    fecha_ultima_limpieza = models.DateField(blank=True, null=True, verbose_name="Fecha de la Última Limpieza")

    general_notes = models.TextField(blank=True, null=True, verbose_name="Notas Generales")
    is_checked = models.BooleanField(default=False, verbose_name='¿Está revisado?')
    is_visible = models.BooleanField(default=False, verbose_name='¿Está Visible?')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Auditoría de Equipo de Computo"
        verbose_name_plural = "Auditoría de Equipos de Computo"
        ordering = ['-created_at']

    def __str__(self):
        return f"Auditoría - {self.created_at.strftime('%Y-%m-%d')}"
    
class ComputerEquipment_Responsiva(models.Model):
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Área del responsable")
    items = models.TextField(blank=True, null=True, verbose_name='Items')
    record = models.TextField(blank=True, null=True, verbose_name='Historial')
    responsibility_letter = models.FileField(upload_to='doc/responsibility_letter/', blank=True, null=True, verbose_name='Responsiva')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Responsiva de Equipo de Computo"
        verbose_name_plural = "Responsivas de Equipos de Computo"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Responsiva de {self.responsible}"
    
class ComputerEquipment_Deliveries(models.Model):
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable")
    items = models.TextField(blank=True, null=True, verbose_name='Items')
    responsibility_letter = models.FileField(upload_to='doc/responsibility_letter/', blank=True, null=True, verbose_name='Responsiva')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Entrega de Equipo de Computo"
        verbose_name_plural = "Entregas de Equipos de Computo"

    def __str__(self):
        return f"Entrega de equipo"
    
# Todo ----- [ 3ro ] -----

class Infrastructure(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable")
    type = models.TextField(blank=True, null=True, verbose_name="Tipo de infraestructura", help_text="ej. servidor, router, switch, etc")
    state = models.TextField(blank=True, null=True, verbose_name="Estado", help_text="ej. activo, inactivo, en mantenimiento, etc.")
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Infraestructura"
        verbose_name_plural = "Infraestructura"

    def __str__(self):
        return f"Infrastructure"
    

class Vehicle_fuel(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Vehículo")
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable")
    payment_receipt = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="Recibo de pago")
    fuel = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, blank=True, null=True, verbose_name="Gasolina (Litros)")
    fuel_type = models.TextField(blank=True, null=True, verbose_name="Tipo de Combustible")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Costo')
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    date = models.DateField(blank=True, null=True, verbose_name='Fecha de rellenado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Gasolina del Vehículo"
        verbose_name_plural = "Gasolina de Vehículos"

    def __str__(self):
        return f"Gasolina"

# Todo ----- [ 3ro ] -----
    
class Infrastructure_Category(models.Model):
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    name = models.CharField(blank=True, null=True, max_length=128, verbose_name="Nombre")
    short_name = models.CharField(blank=True, null=True, max_length=48, verbose_name="Nombre Corto")
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Categoría de Infraestructura"
        verbose_name_plural = "Categorías de Infraestructura"
        ordering = ['name']

    def _str_(self):
        return f"Infraestructura de {self.short_name}"

class Items_locations(models.Model):
    name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre")
    status = models.BooleanField(default=True, verbose_name="¿Está activa la ubicación?")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True) 
  

class Infrastructure_Item(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    category = models.ForeignKey(Infrastructure_Category, on_delete=models.CASCADE, verbose_name="categoría", related_name='items')
    name = models.CharField(max_length=128, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Costo')
    start_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    technical_sheet = models.FileField(upload_to='docs/Equipments_tools', blank=True, null=True, verbose_name="Ficha tecnica")
    invoice = models.FileField(upload_to='docs/Equipments_tools', blank=True, null=True, verbose_name="Factura")
    image = models.FileField(upload_to='docs/Equipments_tools', blank=True, null=True, verbose_name="Factura")

    location = models.ForeignKey(Items_locations, on_delete=models.CASCADE, verbose_name="Ubicación" ,blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Item de Infraestructura"
        verbose_name_plural = "Items de Infraestructura"
        ordering = ['company_id','name']

    def _str_(self):
        return f"{self.category.name}: {self.name} ({self.quantity}) para {self.time_quantity} {self.time_unit}"


class InfrastructureItemDetail(models.Model):
    item = models.ForeignKey(Infrastructure_Item, on_delete=models.CASCADE, related_name='details')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255) 
    identifier = models.CharField(max_length=255, unique=True)  
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable temporal", blank=True, null=True)
    assignment_date = models.DateField(blank=True, null=True, verbose_name="Fecha de asignación")
    created_at = models.DateTimeField(auto_now_add=True)
    qr_info_infrastructure = models.FileField(upload_to='qrcodes/info/', blank=True, null=True)

    class Meta:
        verbose_name = "Detalle de Item de Infraestructura"
        verbose_name_plural = "Detalles de Items de Infraestructura"

    def __str__(self):
        return f"{self.name} - {self.identifier}"



class Infrastructure_maintenance(models.Model):
    identifier = models.ForeignKey(InfrastructureItemDetail, on_delete=models.CASCADE, verbose_name="Item")
    type_maintenance = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    general_notes = models.TextField(max_length=255, blank=True, null=True)
    actions = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, null=False, default="blank")
    comprobante = models.FileField(upload_to='docs/', blank=True, null=True, help_text="Comprobante de pago o de matenimiento")



class MaintenanceAction(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('preventivo', 'Preventivo'), ('correctivo', 'Correctivo')])
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


#tablas de datos para el modulo de servicios--modulo 5 
#tabla categorias de servicios submodulo num.32
class Services_Category(models.Model):
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    name_category = models.CharField(blank=True, null=True, max_length=100, verbose_name="Nombre")
    short_name_category = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre Corto")
    is_active_category = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    description_category = models.TextField(blank=True, null=True, verbose_name="Descripción")

#tabla servicios submodulo num.33
class Services(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    category_service = models.ForeignKey(Services_Category, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Categoría de servicios" )
    name_service = models.CharField(blank=True, null=True, max_length=50, default='Regular', verbose_name="Nombre servicio")
    description_service = models.TextField(blank=True, null=True, verbose_name="Descripcion Servicio")
    provider_service = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Proveedor")
    start_date_service = models.DateField(blank=True, null=True, verbose_name="Fecha de inicio")
    time_quantity_service = models.PositiveIntegerField(blank=True, null=True, default=1, verbose_name="Cantidad de Tiempo")
    time_unit_service = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('day', 'Día(s)'),
        ('month', 'Mes(es)'),
        ('year', 'Año(s)')
    ], verbose_name="Unidad de Tiempo")
    price_service = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Cantidad de servicios')

#tabla pagos de servicios submodulo num.34
class Payments_Services(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),  # El pago está pendiente
        ('upcoming', 'Próximo'),   # El pago está próximo
        ('unpaid', 'No Pagado'),   # El pago no ha sido realizado
        ('paid', 'Pagado'),        # El pago ha sido realizado
    ]
    
    name_service_payment = models.ForeignKey(Services, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Nombre del servicio")
    proof_payment = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="Comprobante de pago")
    total_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Costo')
    next_date_payment = models.DateField(blank=True, null=True, verbose_name="Próxima fecha de pago")
    status_payment = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Estado de pago")
    email_payment = models.BooleanField(default=False)
    email_payment_unpaid = models.BooleanField(default=False)

#tablas para el modulo de equipos y herramientas--modulo 6 num.6
#tabla categorias
class Equipement_category(models.Model):
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre")
    short_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre Corto")
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def clean(self):
        super().clean()

        # Convertir a minúsculas para validación insensible a mayúsculas y minúsculas
        name_lower = self.name.lower() if self.name else None
        short_name_lower = self.short_name.lower() if self.short_name else None
        #Validación del nombre de la empresa 
        if name_lower and Equipement_category.objects.exclude(pk=self.pk).filter(empresa=self.empresa, name__iexact=name_lower).exists():
            raise ValidationError({'name': 'El nombre ya existe en la base de datos para esta empresa. Ingresa un nombre diferente.'})

        # Validación del nombre corto por empresa
        if short_name_lower and Equipement_category.objects.exclude(pk=self.pk).filter(empresa=self.empresa, short_name__iexact=short_name_lower).exists():
            raise ValidationError({'short_name': 'El nombre corto ya existe en la base de datos para esta empresa. Ingresa un nombre corto diferente.'})


    def save(self, *args, **kwargs):
        self.full_clean()  # Llamar al método clean() antes de guardar
        super().save(*args, **kwargs)

class Equipmets_Tools_locations(models.Model):
    location_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre")
    location_status = models.BooleanField(default=True, verbose_name="¿Está activa la ubicación?")
    location_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True) 
  


#tabla de equipos y herramientas 
class Equipment_Tools(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    equipment_category = models.ForeignKey(Equipement_category, on_delete=models.CASCADE, verbose_name="Categoria" ,related_name='reviews')
    equipment_area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="Area" ,blank=True, null=True)
    equipment_responsible = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable del equipo" ,blank=True, null=True)
    equipment_name = models.CharField(blank=True, null=True, max_length=50, default='Regular', verbose_name="Nombre equipo")
    equipment_type = models.CharField(blank=True, null=True, max_length=50, default='Regular', verbose_name="tipo de equipo")
    equipment_brand = models.CharField(blank=True, null=True, max_length=50, default='Regular', verbose_name="Marca")
    equipment_description = models.TextField(blank=True, null=True, verbose_name="Descripcion")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Costo')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Cantidad')
    equipment_technical_sheet = models.FileField(upload_to='docs/Equipments_tools', blank=True, null=True, verbose_name="Ficha tecnica")
    equipment_location = models.ForeignKey(Equipmets_Tools_locations, on_delete=models.CASCADE, verbose_name="Ubicación" ,blank=True, null=True)

    
#tabla de responsivas
class Equipment_Tools_Responsiva(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    equipment_name = models.ForeignKey(Equipment_Tools, on_delete=models.CASCADE, verbose_name="Equipo" ,related_name='reviews')
    responsible_equipment = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Responsable temporal")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Cantidad')
    status_equipment = models.CharField(max_length=20, blank=True, null=True, verbose_name="Estado del Equipo")
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name="Fecha inicio")       
    fecha_entrega = models.DateField(blank=True, null=True, verbose_name="Fecha Entrega")  
    times_requested_responsiva = models.CharField(blank=True, null=True, max_length=50, default='Regular', verbose_name="Tiempo solicitado")
    signature_responsible = models.FileField(upload_to='docs/Equipments_tools/signatures/', blank=True, null=True, verbose_name="Firma del responsable")
    date_receipt = models.DateField(blank=True, null=True, verbose_name="Fecha de recibido")
    signature_almacen = models.FileField(upload_to='docs/Equipments_tools/signatures/', blank=True, null=True, verbose_name="Firma de almacen")
    comments = models.CharField(blank=True, null=True, max_length=300, default='Regular', verbose_name="Comentarios")
    status_modified = models.BooleanField(default=False, verbose_name="Estado modificado")  # Campo para rastrear modificaciones del estado
    email_responsiva = models.BooleanField(default=False)
    email_responsiva_aceptada = models.BooleanField(default=False)
    email_responsiva_next = models.BooleanField(default=False)
    email_responsiva_late = models.BooleanField(default=False)
    email_responsiva_date = models.BooleanField(default=False)






#tabla de planes
class Plans(models.Model):
    STATUS_CHOICES = [
        ('basic', 'Basico'), 
        ('advanced', 'Avanzado'),  
        ('premium', 'Premium'),   
        ('elite', 'Elite'),
        ('esential', 'Esential')
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, blank=True, null=True,verbose_name="Módulos")
    start_date_plan = models.DateField(blank=True, null=True, verbose_name="Fecha de inicio")
    type_plan = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Tipo de plan")
    status_payment_plan = models.BooleanField(default=False, verbose_name="Estado de pago") 
    time_quantity_plan= models.PositiveIntegerField(blank=True, null=True, default=1, verbose_name="Cantidad de Tiempo")
    time_unit_plan = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('day', 'Día(s)'),
        ('month', 'Mes(es)'),
        ('year', 'Año(s)')
    ], verbose_name="Unidad de Tiempo")
    end_date_plan = models.DateField(blank=True, null=True, verbose_name="Fecha de fin")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True, verbose_name='Costo total')
    
class StripeProducts(models.Model):
    name = models.CharField(max_length=254, blank=True, null=True)
    stripedID = models.CharField(max_length=44, blank=True, null=False)
    description = models.CharField(max_length=254, blank=True, null=False)
    tagPrice = models.DecimalField(max_digits=9, decimal_places=2, null=False)
    price = models.DecimalField(max_digits=9, decimal_places=0, null=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"products {self.name}"
#agregar a admin.py para poder visualizarlos en el administrador 











