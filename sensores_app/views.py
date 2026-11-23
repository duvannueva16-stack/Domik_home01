from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dispositivo, Luz, Sensor, Camara, LecturaSensor, Apartamento
from .forms import DispositivoForm, LuzForm, SensorForm, CamaraForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest   

@login_required
@require_POST
def cambiar_brillo(request, pk):
    luz = get_object_or_404(Luz, pk=pk, dispositivo__zona__apartamento__usuario=request.user)
    try:
        valor = int(request.POST.get('brillo'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Brillo inválido')
    if not (0 <= valor <= 100):
        return HttpResponseBadRequest('El brillo debe estar entre 0 y 100')
    luz.brillo = valor
    luz.save()
    return redirect('luces')



@login_required
@require_POST
def alternar_luz(request, pk):
    luz = get_object_or_404(Luz, pk=pk, dispositivo__zona__apartamento__usuario=request.user)
    luz.estado = not luz.estado
    luz.save()
    return redirect('luces')
    
    


def landing(request):
    return render(request, 'landing.html')


@login_required
def index(request):
    """
    Vista de la pantalla de inicio (/inicio/).

    Consulta los datos del usuario autenticado y los envía a index.html:
    - Conteos: luces totales, luces encendidas y cámaras grabando.
    - Últimas lecturas de temperatura, humedad y CO2.
    - Estado de conexión de los dispositivos.
    - Datos del saludo: apartamento, nombre e iniciales.

    Todas las consultas filtran por dispositivo__zona__apartamento__usuario,
    así cada usuario ve solo los datos de su propio apartamento.
    Requiere sesión iniciada (@login_required).
    """
    luces_total = Luz.objects.filter(
        dispositivo__zona__apartamento__usuario=request.user
    ).count()
    luces_on = Luz.objects.filter(
        dispositivo__zona__apartamento__usuario=request.user, estado=True
    ).count()
    camaras_grabando = Camara.objects.filter(
        dispositivo__zona__apartamento__usuario=request.user, grabando=True
    ).count()

    lecturas = LecturaSensor.objects.filter(
        sensor__dispositivo__zona__apartamento__usuario=request.user
    ).order_by('-fecha_hora')
    ultima_temp = lecturas.filter(tipo_magnitud='temperatura').first()
    ultima_hum = lecturas.filter(tipo_magnitud='humedad').first()
    ultimo_co2 = lecturas.filter(tipo_magnitud='co2').first()

    temperatura = ultima_temp.valor if ultima_temp else None
    humedad = ultima_hum.valor if ultima_hum else None
    co2 = ultimo_co2.valor if ultimo_co2 else None

    apartamento = Apartamento.objects.filter(usuario=request.user).first()
    nombre = request.user.first_name or request.user.username
    iniciales = nombre[:2].upper()

    dispositivos = Dispositivo.objects.filter(zona__apartamento__usuario=request.user)
    total = dispositivos.count()
    conectados = dispositivos.filter(estado_conexion=True).count()
    sin_conexion = ', '.join(d.nombre for d in dispositivos.filter(estado_conexion=False))
    cuadros = ['morado' if d.estado_conexion else 'apagado' for d in dispositivos]

    sensores_off = Sensor.objects.filter(
        dispositivo__zona__apartamento__usuario=request.user,
        dispositivo__estado_conexion=False
    ).count()

    return render(request, 'index.html', {
        'luces_total': luces_total,
        'luces_on': luces_on,
        'camaras_grabando': camaras_grabando,
        'temperatura': temperatura,
        'humedad': humedad,
        'co2': co2,
        'apartamento': apartamento,
        'nombre': nombre,
        'iniciales': iniciales,
        'total': total,
        'conectados': conectados,
        'sin_conexion': sin_conexion,
        'cuadros': cuadros,
        'sensores_off': sensores_off,
    })
    
@login_required
def luces(request):
    luces = Luz.objects.select_related('dispositivo', 'dispositivo__zona').filter(
            dispositivo__zona__apartamento__usuario=request.user
        )
    return render(request, 'luces.html', {'luces': luces})
    


@login_required
def sensores(request):
    lecturas = LecturaSensor.objects.select_related('sensor__dispositivo').filter( sensor__dispositivo__zona__apartamento__usuario=request.user).order_by('-fecha_hora')[:20]
    return render(request, 'sensores.html', {'lecturas': lecturas})

@login_required
def camaras(request):
    camaras = Camara.objects.select_related('dispositivo', 'dispositivo__zona').filter(
        dispositivo__zona__apartamento__usuario=request.user
    )
    return render(request, 'camaras.html', {'camaras': camaras})


# ==================== CRUD DISPOSITIVO ====================
@login_required
def lista_dispositivos(request):
    dispositivos = Dispositivo.objects.select_related('zona').filter(
        zona__apartamento__usuario=request.user
    )
    return render(request, 'dispositivos/lista.html', {'dispositivos': dispositivos})


@login_required
def crear_dispositivo(request):
    if request.method == 'POST':
        form = DispositivoForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_dispositivos')
    else:
        form = DispositivoForm(usuario=request.user)
    return render(request, 'dispositivos/crear.html', {'form': form})


@login_required
def editar_dispositivo(request, id):
    dispositivo = get_object_or_404(
        Dispositivo, id=id, zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        form = DispositivoForm(request.POST, instance=dispositivo, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_dispositivos')
    else:
        form = DispositivoForm(instance=dispositivo, usuario=request.user)
    return render(request, 'dispositivos/editar.html', {'form': form, 'dispositivo': dispositivo})


@login_required
def eliminar_dispositivo(request, id):
    dispositivo = get_object_or_404(
        Dispositivo, id=id, zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        dispositivo.delete()
        return redirect('lista_dispositivos')
    return render(request, 'dispositivos/eliminar.html', {'dispositivo': dispositivo})


# ==================== CRUD LUZ ====================
@login_required
def lista_luces(request):
    luces = Luz.objects.select_related('dispositivo', 'dispositivo__zona').filter(
        dispositivo__zona__apartamento__usuario=request.user
    )
    return render(request, 'luces/lista.html', {'luces': luces})


@login_required
def crear_luz(request):
    if request.method == 'POST':
        form = LuzForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_luces')
    else:
        form = LuzForm(usuario=request.user)
    return render(request, 'luces/crear.html', {'form': form})


@login_required
def editar_luz(request, id):
    luz = get_object_or_404(
        Luz, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        form = LuzForm(request.POST, instance=luz, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_luces')
    else:
        form = LuzForm(instance=luz, usuario=request.user)
    return render(request, 'luces/editar.html', {'form': form, 'luz': luz})


@login_required
def eliminar_luz(request, id):
    luz = get_object_or_404(
        Luz, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        luz.delete()
        return redirect('lista_luces')
    return render(request, 'luces/eliminar.html', {'luz': luz})


# ==================== CRUD SENSOR ====================
@login_required
def lista_sensores(request):
    sensores = Sensor.objects.select_related('dispositivo', 'dispositivo__zona').filter(
        dispositivo__zona__apartamento__usuario=request.user
    )
    return render(request, 'sensores/lista.html', {'sensores': sensores})


@login_required
def crear_sensor(request):
    if request.method == 'POST':
        form = SensorForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_sensores')
    else:
        form = SensorForm(usuario=request.user)
    return render(request, 'sensores/crear.html', {'form': form})


@login_required
def editar_sensor(request, id):
    sensor = get_object_or_404(
        Sensor, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        form = SensorForm(request.POST, instance=sensor, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_sensores')
    else:
        form = SensorForm(instance=sensor, usuario=request.user)
    return render(request, 'sensores/editar.html', {'form': form, 'sensor': sensor})


@login_required
def eliminar_sensor(request, id):
    sensor = get_object_or_404(
        Sensor, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        sensor.delete()
        return redirect('lista_sensores')
    return render(request, 'sensores/eliminar.html', {'sensor': sensor})


# ==================== CRUD CAMARA ====================

@login_required
def lista_camara(request):
    camara = Camara.objects.select_related('dispositivo', 'dispositivo__zona').filter(
        dispositivo__zona__apartamento__usuario=request.user
    )
    return render(request, 'camara/lista.html', {'camara': camara})


@login_required
def crear_camara(request):
    if request.method == 'POST':
        form = CamaraForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_camara')
    else:
        form = CamaraForm(usuario=request.user)
    return render(request, 'camara/crear.html', {'form': form})


@login_required
def editar_camara(request, id):
    camara = get_object_or_404(
        Camara, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        form = CamaraForm(request.POST, instance=camara, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('lista_camara')
    else:
        form = CamaraForm(instance=camara, usuario=request.user)
    return render(request, 'camara/editar.html', {'form': form, 'camara': camara})


@login_required
def eliminar_camara(request, id):
    camara = get_object_or_404(
        Camara, id=id, dispositivo__zona__apartamento__usuario=request.user
    )
    if request.method == 'POST':
        camara.delete()
        return redirect('lista_camara')
    return render(request, 'camara/eliminar.html', {'camara': camara})