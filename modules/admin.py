from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(Vehicle_Tenencia)
admin.site.register(Vehicle_Refrendo)
admin.site.register(Vehicle_Verificacion)
admin.site.register(Vehicle_Responsive)
admin.site.register(Vehicle_Insurance)
admin.site.register(Vehicle_Audit)
admin.site.register(Vehicle_Maintenance)
admin.site.register(Vehicle_fuel)
admin.site.register(Vehicle_Maintenance_Kilometer)

admin.site.register(ComputerSystem)
admin.site.register(ComputerPeripheral)
admin.site.register(Software)
admin.site.register(SoftwareInstallation)
admin.site.register(ComputerEquipment_Maintenance)

@admin.register(ComputerEquipment_Audit)

class ComputerEquipment_AuditAdmin(admin.ModelAdmin):
    list_display = ('computerSystem', 'audit_date', 'is_checked', 'is_visible')
    search_fields = ('computerSystem__name', 'audit_date')
    list_filter = ('audit_date', 'is_checked', 'is_visible')
    
admin.site.register(ComputerEquipment_Responsiva)
admin.site.register(ComputerEquipment_Deliveries)
admin.site.register(Infrastructure)

@admin.register(Infrastructure_Category)
class InfrastructureCategoryAdmin(admin.ModelAdmin):
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'short_name', 'description')

@admin.register(Infrastructure_Item)
class InfrastructureItemAdmin(admin.ModelAdmin):
    list_filter = ('company', 'is_active', 'created_at', 'category')
    search_fields = ('name', 'description')

@admin.register(Infrastructure_Review)
class InfrastructureReviewAdmin(admin.ModelAdmin):
    list_filter = ('category', 'checked')
    search_fields = ('checked', 'notes')

#tabla-equipos y herramientas
admin.site.register(Equipement_category)
admin.site.register(Equipment_Tools)
admin.site.register(Equipment_Tools_Responsiva)
admin.site.register(Equipmets_Tools_locations)

#tablas del modulo de servicios 
admin.site.register(Services_Category)
admin.site.register(Services)
admin.site.register(Payments_Services)

admin.site.register(Plans)