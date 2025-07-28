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


@admin.register(InfrastructureItemDetail)
class InfrastructureItemDetailAdmin(admin.ModelAdmin):
    list_display = ('id',)
    search_fields = ('id',)


# @admin.register(Infrastructure_Review)
# class InfrastructureReviewAdmin(admin.ModelAdmin):
#     list_filter = ('category', 'checked')
#     search_fields = ('checked', 'notes')

#tabla-equipos y herramientas
admin.site.register(Equipement_category)
admin.site.register(Equipment_Tools)
admin.site.register(Equipment_Tools_Responsiva)
admin.site.register(Equipmets_Tools_locations)

#tablas del modulo de servicios 
admin.site.register(Services_Category)
admin.site.register(Services)
admin.site.register(Payments_Services)

#tabla de consuctores de vehiculos 
admin.site.register(Vehicle_Driver)
admin.site.register(Licences_Driver)
admin.site.register(Multas)
admin.site.register(Checks)


# admin.site.register(Plans)
admin.site.register(Items_locations)
admin.site.register(Infrastructure_maintenance)
admin.site.register(MaintenanceAction)

@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'module', 'type_plan', 'status_payment_plan',
        'start_date_plan', 'end_date_plan', 'total'
    )
    list_filter = ('type_plan', 'status_payment_plan', 'time_unit_plan', 'start_date_plan')
    search_fields = ('company__name', 'module__name')  # Asume que Company y Module tienen campo 'name'
    date_hierarchy = 'start_date_plan'
    ordering = ('-start_date_plan',)

@admin.register(StripeProducts)
class StripeProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'stripedID', 'description', 'tagPrice', 'price', 'active', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'description', 'stripedID')
    ordering = ('-created_at',)

admin.site.register(Placas)
admin.site.register(Facturas_Vehicle)
admin.site.register(Card_Vehicle)
admin.site.register(Contract_Vehicle)
admin.site.register(Letter_Facturas_Vehicle)    
admin.site.register(Hologram_Vehicle)
admin.site.register(Carnet_Vehicle)