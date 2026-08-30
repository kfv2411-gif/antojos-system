from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>¡Bienvenida a Antojos by Dulce Delicias!</h1><p>Espacio de trabajo para Brenda y Kalena.</p><p><a href='/admin/'>Ir al Panel de Administración</a></p>")