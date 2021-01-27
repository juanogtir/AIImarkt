#encoding:utf-8

from django.db import models
from enum import Enum
from django.core.validators import MinValueValidator,MaxValueValidator,URLValidator

class PieChoice(Enum):
    IZQ="izquierdo"
    DER="derecho"
    AMB="ambidiestro"
    IND="indeterminado"
    
    def __str__(self):
        return self.value

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
    foto_jugador=models.URLField(verbose_name='URL de la foto del jugador')

    pie=models.CharField(max_length=3,verbose_name='Pie',choices=[(tag,tag.value) for tag in PieChoice])

    posicion_principal=models.ForeignKey(PosicionPrincipal,on_delete=models.DO_NOTHING)
    posiciones_secundarias=models.ManyToManyField(PosicionSecundaria)

    nacionalidades=models.ManyToManyField(Pais)

    equipo=models.ForeignKey(Equipo,on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre+" ("+str(self.edad)+")"
    class Meta:
        ordering = ('nombre', 'valor','idJugador')
        db_table = "Jugadores"

class Profesion(models.Model):
    numero = models.IntegerField(verbose_name='Numero de la profesion',default=1)
    nombre = models.TextField(verbose_name='Nombre de la profesion')
    
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre',)
        db_table = "Profesiones"
        
class Usuario(models.Model):
    numUsuario=models.IntegerField(verbose_name='Numero de usuario',default=1,null=True)
    edad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    genero = models.CharField(max_length=1, choices=(('F', 'Femenino'),('M','Masculino'),))
    equipo_favorito=models.ForeignKey(Equipo, on_delete=models.DO_NOTHING)
    profesion = models.ForeignKey(Profesion, on_delete=models.DO_NOTHING)
    zipCode = models.CharField(max_length=8)

    def __str__(self):
        return self.genero+" "+str(self.zipCode)
    class Meta:
        ordering = ('numUsuario',)
        db_table = "Usuarios"

class Puntuacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    jugador = models.ForeignKey(Jugador, on_delete=models.DO_NOTHING)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    def __str__(self):
        return str(self.rating)+" "+self.jugador.nombre