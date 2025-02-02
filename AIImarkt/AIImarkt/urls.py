"""AIImarkt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main import views
from main import views_rs

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('',views.index),
    path('error',views_rs.redirect_error),

    path('ingresar',views.ingresar),
    path('cerrar',views.cerrar),
    path('privado',views.privado),
    path('usuarionuevo',views.usuario_nuevo),

    path('populate/', views.populateDatabase),
    
    path('whoosh/', views.index_whoosh),
    path('whoosh/buscar_posicion_valor', views.whoosh_buscar_posicion_valor),
    path('whoosh/buscar_nacionalidad', views.whoosh_buscar_nacionalidad),
    path('whoosh/buscar_contrato', views.whoosh_buscar_contrato), 
    
    path('listado_equipos/', views.lista_equipos),  
    path('listado_jugadores/', views.lista_jugadores_por_equipo),
    
    path('rs/', views.index_rs),
    path('rs/populate/', views_rs.datos_RS),
    path('rs/loadRecsys/', views_rs.loadRS),
    path('rs/recomendar_jugadorU/', views_rs.recomendarJugadoresUsuario),
    path('rs/recomendar_jugadorI/', views_rs.recomendarJugadoresItem),
    path('rs/similar_jugador/', views_rs.jugadoresSimilares),
    path('rs/recomendar_usuarios/', views_rs.recomendarUsuariosAJugadores),
]

