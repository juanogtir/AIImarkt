#encoding:utf-8
from main.models import Jugador,Equipo,Pais,PieChoice,PosicionPrincipal,PosicionSecundaria
from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaYearForm
from django.shortcuts import render, HttpResponse
from django.template import RequestContext
from django.db.models import Avg
from django.http.response import HttpResponseRedirect
from django.conf import settings

from main import aiimarkt_utils

def populateDatabase(request):
    aiimarkt_utils.populate()
    return HttpResponseRedirect('/index.html')