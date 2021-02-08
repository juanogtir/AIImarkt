# encoding:utf-8

from main.models import Jugador, Equipo
from main.forms import  PosicionValorBusquedaForm, NacionalidadBusquedaForm, ContratoBusquedaForm, ListadoEquiposForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect

from django.http.response import HttpResponseRedirect
from django.conf import settings

from main import aiimarkt_utils

# Gestion de usuarios
def ingresar(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect('/privado')
    if request.method == 'POST':
        formulario = AuthenticationForm(request.POST)
        if formulario.is_valid:
            usuario = request.POST['username']
            clave = request.POST['password']
            acceso = authenticate(username=usuario, password=clave)
            if acceso is not None:
                if acceso.is_active:
                    login(request, acceso)
                    return HttpResponseRedirect('/privado')
                else:
                    return render(request, 'noactivo.html')
            else:
                return render(request, 'nousuario.html')
    else:
        formulario = AuthenticationForm()
    context = {'formulario': formulario}
    return render(request, 'ingresar.html', context)

def usuario_nuevo(request):
    if request.method=='POST':
        formulario = UserCreationForm(request.POST)
        if formulario.is_valid:
            formulario.save()
            return HttpResponseRedirect('/')
    else:
        formulario = UserCreationForm()
    context = {'formulario': formulario}
    return render(request, 'nuevousuario.html', context)

@login_required(login_url='/ingresar')
def privado(request):
    usuario = request.user
    context = {'usuario': usuario}
    return render(request, 'privado.html', context)

@login_required(login_url='/ingresar')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/')
#######################################################################################################

def index(request):
    return render(request, 'index.html', {'STATIC_URL':settings.STATIC_URL})

def index_whoosh(request):
    return render(request, 'index_whoosh.html', {'STATIC_URL':settings.STATIC_URL})

def index_rs(request):
    return render(request, 'index_rs.html', {'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/ingresar')
def populateDatabase(request):
    if request.method=='POST':
        if 'Aceptar' in request.POST:     
            aiimarkt_utils.populate()
            num_jugadores=Jugador.objects.count()
            num_equipos=Equipo.objects.count()
            mensaje="Se han almacenado: " + str(num_jugadores) +" jugadores de " + str(num_equipos) +" equipos"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
    return render(request, 'confirmacion.html', {'STATIC_URL':settings.STATIC_URL})

# DJANGO

def lista_equipos(request):
    equipos = Equipo.objects.all().order_by("-valor",)
    result = []
    for equipo in equipos:
        try:
            capitan = Jugador.objects.get(equipo=equipo.idEquipo, capitan=True)
        except:
            capitan = "Ninguno"
        result.append((equipo, capitan))
    
    return render(request, 'lista_equipos.html', {'equipos':result, 'STATIC_URL':settings.STATIC_URL})


def lista_jugadores_por_equipo(request):
    formulario = ListadoEquiposForm()
    equipo_form = None
    jugadores_result = None
    if request.method == 'POST':
        formulario = ListadoEquiposForm(request.POST)
        if formulario.is_valid():
            
            equipo_form = formulario.cleaned_data['equipo']
            equipo = Equipo.objects.get(nombre=equipo_form)
            
            jugadores_result = Jugador.objects.all().order_by("-valor",).filter(equipo=equipo)
            if jugadores_result == None:
                jugadores_result = []
            
    return render(request, 'listado_jugador_por_equipo.html', {'formulario':formulario, 'jugadores':jugadores_result, 'equipo_seleccionado':equipo_form, 'STATIC_URL':settings.STATIC_URL})


# WHOOSH

def whoosh_buscar_posicion_valor(request):
    formulario = PosicionValorBusquedaForm()

    jugadores_result = None
    if request.method == 'POST':
        formulario = PosicionValorBusquedaForm(request.POST)
        
        if formulario.is_valid():
            
            rango1 = formulario.cleaned_data['rango1']
            rango2 = formulario.cleaned_data['rango2']
            posicion = formulario.cleaned_data['posicion']
            jugadores_result = aiimarkt_utils.buscar_posicion_valor(posicion, rango1, rango2)
            if jugadores_result == None:
                jugadores_result = []
            
    return render(request, 'busqueda_whoosh.html', {'formulario':formulario, 'jugadores':jugadores_result, 'STATIC_URL':settings.STATIC_URL})


def whoosh_buscar_nacionalidad(request):
    formulario = NacionalidadBusquedaForm()

    jugadores_result = None
    if request.method == 'POST':
        formulario = NacionalidadBusquedaForm(request.POST)
        
        if formulario.is_valid():
            
            nacionalidad = formulario.cleaned_data['nacionalidad']
            jugadores_result = aiimarkt_utils.buscar_nacionalidad(nacionalidad)
            if jugadores_result == None:
                jugadores_result = []
            
    return render(request, 'busqueda_whoosh.html', {'formulario':formulario, 'jugadores':jugadores_result, 'STATIC_URL':settings.STATIC_URL})


def whoosh_buscar_contrato(request):
    formulario = ContratoBusquedaForm()

    jugadores_result = None
    if request.method == 'POST':
        formulario = ContratoBusquedaForm(request.POST)
        
        if formulario.is_valid():
            fecha = formulario.cleaned_data['fecha']
            jugadores_result = aiimarkt_utils.buscar_contrato(fecha)
            if jugadores_result == None:
                jugadores_result = []
            
    return render(request, 'busqueda_whoosh.html', {'formulario':formulario, 'jugadores':jugadores_result, 'STATIC_URL':settings.STATIC_URL})
