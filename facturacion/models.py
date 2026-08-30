from django.db import models
from django.contrib.auth.models import User

class ConfiguracionNegocio(models.Model):
    nombre_negocio = models.CharField(max_length=150, default="Antojos by Dulce Delicias")
    logotipo = models.ImageField(upload_to='logos/', blank=True, null=True)
    color_primario = models.CharField(max_length=7, default="#FF5733")
    color_secundario = models.CharField(max_length=7, default="#33FF57")
    
    def __str__(self):
        return self.nombre_negocio

class Empleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50) # Ej: Cajera, Administrador
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.cargo})"

class TurnoCaixa(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    abierta = models.BooleanField(default=True)

    def __str__(self):
        return f"Caja de {self.empleado.usuario.username} - Turno: {self.fecha_apertura.strftime('%Y-%m-%d %H:%M')}"

class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    documento_identidad = models.CharField(max_length=20, unique=True) # RNC o Cédula
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.documento_identidad}"

class ProductoInventario(models.Model):
    nombre = models.CharField(max_length=150)
    unidad_medida = models.CharField(max_length=20) # Ej: kg, litros, gramos, unidad
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            anterior = ProductoInventario.objects.get(pk=self.pk)
            if anterior.costo_unitario != self.costo_unitario:
                super().save(*args, **kwargs)
                recetas_afectadas = DetalleReceta.objects.filter(ingrediente=self)
                for detalle in recetas_afectadas:
                    detalle.receta.recalcular_costo_total()
                return
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} (Costo: ${self.costo_unitario})"

class PlatoReceta(models.Model):
    nombre = models.CharField(max_length=150)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    disponible = models.BooleanField(default=True)

    def recalcular_costo_total(self):
        detalles = self.detalles.all()
        nuevo_costo = sum(detalle.calcular_costo_parcial() for detalle in detalles)
        self.costo_total = nuevo_costo
        self.save(update_fields=['costo_total'])

    def __str__(self):
        return f"{self.nombre} - Costo: ${self.costo_total} / Venta: ${self.precio_venta}"

class DetalleReceta(models.Model):
    receta = models.ForeignKey(PlatoReceta, related_name='detalles', on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(ProductoInventario, on_delete=models.PROTECT)
    cantidad_necesaria = models.DecimalField(max_digits=10, decimal_places=2)

    def calcular_costo_parcial(self):
        return self.cantidad_necesaria * self.ingrediente.costo_unitario

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.receta.recalcular_costo_total()

    def delete(self, *args, **kwargs):
        receta_obj = self.receta
        super().delete(*args, **kwargs)
        receta_obj.recalcular_costo_total()

class Factura(models.Model):
    turno = models.ForeignKey(TurnoCaixa, on_delete=models.PROTECT)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    enviada_correo = models.BooleanField(default=False)

    def __str__(self):
        return f"Factura #{self.id} - Cliente: {self.cliente.nombre} - Total: ${self.total}"

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name='items', on_delete=models.CASCADE)
    plato = models.ForeignKey(PlatoReceta, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)