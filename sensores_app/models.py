from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings




# ---------------------------------------------------------------
# Listas de opciones (equivalen a los ENUM de PostgreSQL)
# ---------------------------------------------------------------
lista_clase = [
    ('luz', 'Luz'),
    ('sensor', 'Sensor'),
    ('camara', 'Cámara'),
    ('videoportero', 'Videoportero'),
]

lista_evento = [
    ('manual', 'Manual'),
    ('automatico', 'Automático'),
]

lista_magnitud = [
    ('temperatura', 'Temperatura'),
    ('humedad', 'Humedad'),
    ('movimiento', 'Movimiento'),
    ('co2', 'CO2'),
    ('luminosidad', 'Luminosidad'),
]

lista_puerta = [
    ('abierta', 'Abierta'),
    ('cerrada', 'Cerrada'),
]

lista_notificacion = [
    ('llamada', 'Llamada'),
    ('cambio_estado', 'Cambio de estado'),
    ('alerta', 'Alerta'),
    ('movimiento_detectado', 'Movimiento detectado'),
    ('puerta_abierta', 'Puerta abierta'),
    ('bateria_baja', 'Batería baja'),
]

lista_acceso = [
    ('pin', 'PIN'),
    ('rfid', 'RFID'),
    ('app', 'App'),
    ('llave', 'Llave'),
]


# ---------------------------------------------------------------
# Usuario y apartamento
class Apartamento(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    piso = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nombre



class Zona(models.Model):
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre



# Dispositivos

class Dispositivo(models.Model):
    nombre = models.CharField(max_length=50)
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    clase = models.CharField(max_length=15, choices=lista_clase)
    estado_conexion = models.BooleanField(default=False)
    fecha_instalacion = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Luz(models.Model):
    dispositivo = models.OneToOneField(Dispositivo, on_delete=models.CASCADE)
    estado = models.BooleanField(default=False)
    brillo = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    mac_address = models.CharField(max_length=17, unique=True, null=True, blank=True)
    topico_mqtt = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Luz de {self.dispositivo}"


class Sensor(models.Model):
    dispositivo = models.OneToOneField(Dispositivo, on_delete=models.CASCADE)
    mac_address = models.CharField(max_length=17, unique=True)
    topico_mqtt = models.CharField(max_length=150)
    magnitudes_soportadas = models.JSONField(default=list)
    firmware_version = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Sensor de {self.dispositivo}"


class LecturaSensor(models.Model):
    id = models.BigAutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(default=timezone.now)
    tipo_magnitud = models.CharField(max_length=15, choices=lista_magnitud)
    valor = models.DecimalField(max_digits=10, decimal_places=3)
    unidad_medida = models.CharField(max_length=20)

    class Meta:
        indexes = [models.Index(fields=['sensor', 'fecha_hora'])]

    def __str__(self):
        return f"{self.tipo_magnitud}: {self.valor} {self.unidad_medida}"


class Camara(models.Model):
    dispositivo = models.OneToOneField(Dispositivo, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    stream_url = models.CharField(max_length=255, null=True, blank=True)
    resolucion = models.CharField(max_length=20, null=True, blank=True)
    grabando = models.BooleanField(default=False)

    def __str__(self):
        return f"Cámara de {self.dispositivo}"


class Videoportero(models.Model):
    dispositivo = models.OneToOneField(Dispositivo, on_delete=models.CASCADE)
    estado_puerta = models.CharField(max_length=10, choices=lista_puerta, null=True, blank=True)
    tiene_camara_integrada = models.BooleanField(default=True)
    mac_address = models.CharField(max_length=17, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Videoportero de {self.dispositivo}"


# ---------------------------------------------------------------
# Eventos, patrones y consumo
# ---------------------------------------------------------------
class Evento(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    hora_exacta = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=lista_evento)
    estado_anterior = models.CharField(max_length=50, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.dispositivo}: {self.estado_nuevo}"


class Patron(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    hora = models.TimeField()
    accion = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    # Reemplaza la tabla patron_evento (relación muchos a muchos)
    eventos = models.ManyToManyField(Evento, blank=True)

    def __str__(self):
        return f"{self.accion} a las {self.hora}"


class Consumo(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    amperaje = models.DecimalField(max_digits=6, decimal_places=3)
    watts = models.DecimalField(max_digits=8, decimal_places=3)

    class Meta:
        indexes = [models.Index(fields=['dispositivo', 'fecha_hora'])]

    def __str__(self):
        return f"{self.dispositivo}: {self.watts} W"


# ---------------------------------------------------------------
# Notificaciones, accesos y comandos de voz
# ---------------------------------------------------------------
class Notificacion(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    hora = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=20, choices=lista_notificacion)
    foto_url = models.CharField(max_length=255, null=True, blank=True)
    respondida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tipo} - {self.dispositivo}"


class Acceso(models.Model):
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_visitante = models.CharField(max_length=100, null=True, blank=True)
    metodo = models.CharField(max_length=10, choices=lista_acceso)
    fecha_hora = models.DateTimeField(default=timezone.now)
    permitido = models.BooleanField()

    class Meta:
        indexes = [models.Index(fields=['apartamento', 'fecha_hora'])]

    def clean(self):
        # Igual que el CHECK del SQL: debe haber usuario o nombre de visitante
        if self.usuario is None and not self.nombre_visitante:
            raise ValidationError('Debes indicar un usuario o el nombre del visitante.')

    def __str__(self):
        quien = self.usuario.username if self.usuario else self.nombre_visitante
        return f"{quien} ({self.metodo})"


class ComandoVoz(models.Model):
    apartamento = models.ForeignKey(Apartamento, on_delete=models.CASCADE)
    comando_texto = models.CharField(max_length=255)
    origen = models.CharField(max_length=50, null=True, blank=True)
    fecha_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.comando_texto
