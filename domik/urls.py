from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from sensores_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('inicio/', views.index, name='index'),
   

    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Paneles
    path('luces/', views.luces, name='luces'),
    path('sensores/', views.sensores, name='sensores'),
    path('camaras/', views.camaras, name='camaras'),

    # CRUD luces
    path('lista_luces/', views.lista_luces, name='lista_luces'),
    path('lista_luces/nueva/', views.crear_luz, name='crear_luz'),
    path('lista_luces/<int:id>/editar/', views.editar_luz, name='editar_luz'),
    path('lista_luces/<int:id>/eliminar/', views.eliminar_luz, name='eliminar_luz'),
    path('luces/<int:pk>/alternar/', views.alternar_luz, name='alternar_luz'),
    path('luces/<int:pk>/brillo/', views.cambiar_brillo, name='cambiar_brillo'),

    # CRUD dispositivos
    path('lista_dispositivos/', views.lista_dispositivos, name='lista_dispositivos'),
    path('lista_dispositivos/nueva/', views.crear_dispositivo, name='crear_dispositivo'),
    path('lista_dispositivos/<int:id>/editar/', views.editar_dispositivo, name='editar_dispositivo'),
    path('lista_dispositivos/<int:id>/eliminar/', views.eliminar_dispositivo, name='eliminar_dispositivo'),

    # CRUD sensores
    path('lista_sensores/', views.lista_sensores, name='lista_sensores'),
    path('lista_sensores/nueva/', views.crear_sensor, name='crear_sensor'),
    path('lista_sensores/<int:id>/editar/', views.editar_sensor, name='editar_sensor'),
    path('lista_sensores/<int:id>/eliminar/', views.eliminar_sensor, name='eliminar_sensor'),

    # CRUD cámaras
    path('lista_camara/', views.lista_camara, name='lista_camara'),
    path('lista_camara/nueva/', views.crear_camara, name='crear_camara'),
    path('lista_camara/<int:id>/editar/', views.editar_camara, name='editar_camara'),
    path('lista_camara/<int:id>/eliminar/', views.eliminar_camara, name='eliminar_camara'),
]