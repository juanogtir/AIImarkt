#encoding:utf-8

from django.db import models
from enum import Enum

class PieChoice(Enum):
    IZQ="izquierdo"
    DER="derecho"
    AMB="ambidiestro"
    IND="indeterminado"

class PosicionPrincipal(models.Model):
    nombre = models.TextField(verbose_name='Posición principal')
    def __str__(self):
        return self.nombre
    db_table = "PosicionesPrincipales"

class PosicionSecundaria(models.Model):
    nombre = models.TextField(verbose_name='Posición secundaria')
    def __str__(self):
        return self.nombre
    db_table = "PosicionesSecundarias"

class Pais(models.Model):
    nombre = models.TextField(verbose_name='Nacionalidad')
    def __str__(self):
        return self.nombre
    db_table = "Paises"

class Equipo(models.Model):
    idEquipo=models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Equipo')
    valor=models.FloatField(verbose_name='Valor')
    url_escudo=models.URLField(verbose_name='URL del escudo')
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre', 'valor','idEquipo')
        db_table = "Equipos"

class Jugador(models.Model):
    idJugador=models.AutoField(primary_key=True)
    nombre = models.TextField(verbose_name='Jugador')
    edad = models.IntegerField(verbose_name='Edad', help_text='Debe introducir una edad')
    altura=models.FloatField(verbose_name='Altura')
    valor=models.FloatField(verbose_name='Valor')
    contrato= models.DateField(verbose_name='Contrato')
    capitan=models.BooleanField()

    pie=models.CharField(max_length=3,verbose_name='Pie',choices=[(tag,tag.value) for tag in PieChoice])

    posicion_principal=models.ForeignKey(PosicionPrincipal,on_delete=models.CASCADE)
    posiciones_secundarias=models.ManyToManyField(PosicionSecundaria)

    nacionalidades=models.ManyToManyField(Pais)

    equipo=models.ForeignKey(Equipo,on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre+" ("+self.edad+")"
    class Meta:
        ordering = ('nombre', 'valor','idJugador')
        db_table = "Jugadores"
