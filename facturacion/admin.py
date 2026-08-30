from django.contrib import admin
from .models import (
    ConfiguracionNegocio, Empleado, TurnoCaixa, Cliente, 
    ProductoInventario, PlatoReceta, DetalleReceta, Factura, DetalleFactura
)

admin.site.register(ConfiguracionNegocio)
admin.site.register(Empleado)
admin.site.register(TurnoCaixa)
admin.site.register(Cliente)
admin.site.register(ProductoInventario)

class DetalleRecetaInline(admin.TabularInline):
    model = DetalleReceta
    extra = 1

@admin.register(PlatoReceta)
class PlatoRecetaAdmin(admin.ModelAdmin):
    inlines = [DetalleRecetaInline]
    readonly_fields = ('costo_total',)

admin.site.register(Factura)
admin.site.register(DetalleFactura)
