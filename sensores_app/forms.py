from django import forms
from .models import Dispositivo, Zona, Luz, Sensor, Camara


class DispositivoForm(forms.ModelForm):
    class Meta:
        model = Dispositivo
        fields = ['nombre', 'zona', 'clase']

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario')
        super().__init__(*args, **kwargs)
        self.fields['zona'].queryset = Zona.objects.filter(apartamento__usuario=usuario)
        
class LuzForm(forms.ModelForm):
    class Meta:
        model = Luz
        fields = ['dispositivo', 'brillo', 'estado', 'mac_address', 'topico_mqtt']
        
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario')
        super().__init__(*args, **kwargs)
        self.fields['dispositivo'].queryset = Dispositivo.objects.filter(zona__apartamento__usuario=usuario)
            

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['dispositivo', 'mac_address', 'topico_mqtt', 'magnitudes_soportadas', 'firmware_version']
    
    def __init__(self, *args, **kwargs): 
        usuario = kwargs.pop('usuario')
        super().__init__(*args, **kwargs)
        self.fields['dispositivo'].queryset = Dispositivo.objects.filter(zona__apartamento__usuario=usuario)
    
    
class CamaraForm(forms.ModelForm):
    class Meta:
        model = Camara 
        fields = ['dispositivo', 'ip_address', 'stream_url', 'resolucion', 'grabando']
        
    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario')
        super().__init__(*args, **kwargs)
        self.fields['dispositivo'].queryset = Dispositivo.objects.filter(zona__apartamento__usuario=usuario)
            