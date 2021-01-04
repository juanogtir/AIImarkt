# encoding:utf-8
from django import forms
from main.models import Jugador, Equipo, Pais, PieChoice, PosicionPrincipal, PosicionSecundaria
from main import aiimarkt_utils
import datetime

   
class PosicionValorBusquedaForm(forms.Form):
    choices = aiimarkt_utils.lista_posiciones_principales_secundarias()
    rango1 = forms.CharField(label="Rango inferior", widget=forms.TextInput(attrs={'type':'number'}), required=True, initial="20")
    rango2 = forms.CharField(label="Rango superior", widget=forms.TextInput(attrs={'type':'number'}), required=True, initial="50")
    if choices != None:
        posicion = forms.ChoiceField(label="Posicion", choices=choices)


class NacionalidadBusquedaForm(forms.Form):
    choices = aiimarkt_utils.lista_nacionalidades()
    if choices != None:
        nacionalidad = forms.ChoiceField(label="Nacionalidad", choices=choices)

    
class ContratoBusquedaForm(forms.Form):
    fecha = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'placeholder': 'DD/MM/YYYY', 'required': 'required'}))


class ListadoEquiposForm(forms.Form):
    choices = aiimarkt_utils.lista_equipos()
    if choices != None:
        equipo = forms.ChoiceField(label="Equipo", choices=choices)
