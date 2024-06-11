from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField()
    def __str__(self):
        return f"{self.name}"

class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.name
    
class Area(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Código del Área", help_text="Código único para identificar el área")
    name = models.CharField(max_length=64, verbose_name="Nombre del Área")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción del Área")
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self):
        return self.name
    
class Provider(models.Model):
    name = models.CharField(max_length=64)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="¿Está Activo?")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return f"{self.company.name}: {self.name}"

class User_Access(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    #updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    class Meta:
        verbose_name = "Acceso de Usuario"
        verbose_name_plural = "Accesos de usuarios"

    def __str__(self):
        return f"[{self.company}]: el usuario '{self.user}' es {self.role}"

class Module(models.Model):
    short_name = models.CharField(max_length=32, null=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SubModule(models.Model):
    is_active = models.BooleanField(default=True)
    short_name = models.CharField(max_length=32, null=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=128, null=True, blank=True)
    module = models.ForeignKey(Module, related_name='submodules', on_delete=models.CASCADE)
    icon = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    superUserExclusive = models.BooleanField(default=False, help_text="Exclusivo para SuperUsuario")
    
    def __str__(self):
        return f"{self.module.name}: {self.name}"

class SubModule_Permission(models.Model):
    subModule = models.ForeignKey(
        SubModule,
        related_name='permissions',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    user = models.ForeignKey(User_Access, on_delete=models.CASCADE)
    create = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    #updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")

    def __str__(self):
        return f"Permisos de {self.user} en el submódulo: {self.subModule}"
