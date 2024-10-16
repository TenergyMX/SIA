from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import *
from datetime import datetime, timedelta

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
    mileage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)   # Kilometraje
    insurance_company = models.CharField(max_length=100, blank=True, null=True)             # Aseguradora
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
    
class Vehicle_Tenencia(models.Model):
    vehiculo = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_pago = models.DateField()
    comprobante_pago = models.FileField(upload_to='docs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"Verificación vehicular para {self.vehiculo}"
    
class Vehicle_Responsive(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    responsible = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    image_path_entry_1 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_entry_2 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_exit_1 = models.FileField(upload_to='docs/', blank=True, null=True)
    image_path_exit_2 = models.FileField(upload_to='docs/', blank=True, null=True)
    initial_mileage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    final_mileage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
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

    def __str__(self):
        return self.policy_number
    
class Vehicle_Audit(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    audit_date = models.DateField()
    check_interior = models.CharField(max_length=20, blank=True, null=True)
    notes_interior = models.TextField(blank=True, null=True)
    check_exterior = models.CharField(max_length=20, blank=True, null=True)
    notes_exterior = models.TextField(blank=True, null=True)
    check_tires = models.CharField(max_length=20, blank=True, null=True)
    notes_tires = models.TextField(blank=True, null=True)
    check_antifreeze_level = models.CharField(max_length=20, blank=True, null=True)
    check_fuel_level = models.CharField(max_length=20, blank=True, null=True)
    general_notes = models.TextField(blank=True, null=True)
    is_checked = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auditoría de {self.vehicle} el {self.audit_date}"
    
    class Meta:
        verbose_name = 'Auditoría de Vehículo'
        verbose_name_plural = 'Auditoría de Vehículos'
    
class Vehicle_Maintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mileage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    time = models.CharField(max_length=100, blank=True, null=True, help_text="Tiempo")
    general_notes = models.TextField(max_length=255, blank=True, null=True)
    actions = models.TextField(blank=True, null=True)
    comprobante = models.FileField(upload_to='docs/', blank=True, null=True, help_text="Comprobante de pago o de matenimiento")
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle} - {self.type} - {self.date}"
    
    class Meta:
        verbose_name = 'Mantenimiento de Vehículo'
        verbose_name_plural = 'Mantenimiento de Vehículos'
    

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

    class Meta:
        verbose_name = "Equipo de Computo"
        verbose_name_plural = "Equipos de Computo"

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.brand} {self.model})"
        else:
            return "Equipo sin nombre"
        
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

    class Meta:
        verbose_name = "Periférico de Equipo de Computo"
        verbose_name_plural = "Periféricos de Equipos de Computo"

    def __str__(self):
        if self.name:
            if self.responsible:
                return f"{self.name} ({self.brand} {self.model}) - Asignado a: {self.responsible.username}"
            else:
                return f"{self.name} ({self.brand} {self.model}) - Libre"
        else:
            return "Periférico sin nombre"
        
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
    software_identifier = models.CharField(max_length=100, verbose_name="Identificador del Software", help_text="Identificador del software proporcionado por el proveedor")
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
    name = models.CharField(blank=True, null=True, max_length=128, unique=True, verbose_name="Nombre")
    short_name = models.CharField(blank=True, null=True, max_length=48, unique=True, verbose_name="Nombre Corto")
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
    
class Infrastructure_Item(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Empresa")
    category = models.ForeignKey(Infrastructure_Category, on_delete=models.CASCADE, verbose_name="categoría", related_name='items')
    name = models.CharField(max_length=128, verbose_name="Nombre")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    start_date = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    time_quantity = models.PositiveIntegerField(blank=True, null=True, default=1, verbose_name="Cantidad de Tiempo")
    time_unit = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('day', 'Día(s)'),
        ('month', 'Mes(es)'),
        ('year', 'Año(s)')
    ], verbose_name="Unidad de Tiempo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Item de Infraestructura"
        verbose_name_plural = "Items de Infraestructura"
        ordering = ['company_id','name']

    def _str_(self):
        return f"{self.category.name}: {self.name} ({self.quantity}) para {self.time_quantity} {self.time_unit}"
    
class Infrastructure_Review(models.Model):
    category = models.ForeignKey(Infrastructure_Category, on_delete=models.CASCADE, verbose_name="Categoría" ,related_name='reviews')
    item = models.ForeignKey(Infrastructure_Item, on_delete=models.CASCADE, verbose_name="Item" ,related_name='reviews')
    checked = models.CharField(blank=True, null=True, max_length=20, default='Regular', verbose_name="Check")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    date = models.DateField(blank=True, null=True, verbose_name="Fecha")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='Crítico')
    file = models.FileField(upload_to='docs/', blank=True, null=True, verbose_name="Archivo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "revisión de la Infraestructura"
        verbose_name_plural = "revisiónes de la Infraestructura"

    def _str_(self):
        return f"{self.category.name}: {self.item.name} ({self.checked}) ({self.date})"
    

#tablas para el modulo de equipos y herramientas--
#tabla categorias
class Equipement_category(models.Model):
    name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre")
    short_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre Corto")
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def clean(self):
        super().clean()

        # Convertir a minúsculas para validación insensible a mayúsculas y minúsculas
        name_lower = self.name.lower() if self.name else None
        short_name_lower = self.short_name.lower() if self.short_name else None

        if Equipement_category.objects.exclude(pk=self.pk).filter(name__iexact=name_lower).exists():
            raise ValidationError({'name': 'El nombre ya existe en la base de datos. Ingresa un nombre diferente.'})

        if Equipement_category.objects.exclude(pk=self.pk).filter(short_name__iexact=short_name_lower).exists():
            raise ValidationError({'short_name': 'El nombre corto ya existe en la base de datos. Ingresa un nombre corto diferente.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Llamar al método clean() antes de guardar
        super().save(*args, **kwargs)

class Equipmets_Tools_locations(models.Model):
    location_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="Nombre")
    location_status = models.BooleanField(default=True, verbose_name="¿Está activa la ubicación?")
    location_company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)   


#tabla de equipos y herramientas 
class Equipment_Tools(models.Model):
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

#agregar a admin.py para poder visualizarlos en el administrador 











