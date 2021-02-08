from django.contrib import admin
from main.models import Jugador,Equipo,Pais,PieChoice,PosicionPrincipal,PosicionSecundaria

# Register your models here.
admin.site.register(Jugador)
admin.site.register(Equipo)
admin.site.register(Pais)
#admin.site.register(PieChoice)
admin.site.register(PosicionPrincipal)
admin.site.register(PosicionSecundaria)