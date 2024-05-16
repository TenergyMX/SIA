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
    visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auditoría de {self.vehicle} el {self.audit_date}"
    
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