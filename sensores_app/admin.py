from django.contrib import admin
from .models import (Apartamento, Zona, Dispositivo, Luz, Sensor, LecturaSensor, Camara, Videoportero, Dispositivo, Evento,  Patron, Consumo, Notificacion, Acceso, ComandoVoz)

admin.site.register(Apartamento)
admin.site.register(Zona)
admin.site.register(Dispositivo)
admin.site.register(Luz)
admin.site.register(Sensor)
admin.site.register(LecturaSensor)
admin.site.register(Camara)
admin.site.register(Videoportero)
admin.site.register(Evento)
admin.site.register(Patron)
admin.site.register(Consumo)
admin.site.register(Notificacion)
admin.site.register(Acceso)
admin.site.register(ComandoVoz)

