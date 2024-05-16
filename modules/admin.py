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