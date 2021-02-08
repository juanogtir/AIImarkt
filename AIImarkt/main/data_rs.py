# encoding:utf-8

from main.models import Jugador, Equipo, Profesion,Usuario,Puntuacion
from django.shortcuts import redirect

import numpy as np
from random import randint,choice,choices

NUM_USUARIOS=1000
VOTOS_POR_USUARIO=[50,80]
path = "datos_rs"

def borra_datos_anteriores():
    Puntuacion.objects.all().delete() 
    Usuario.objects.all().delete() 
    Profesion.objects.all().delete()

def elige_equipo_random():
    equipos=list(Equipo.objects.all())
    num_equipos=len(equipos)
    eleccion=randint(0,num_equipos-1)
    return equipos[eleccion]

def elige_profesion_random():
    num_profesiones=Profesion.objects.count()
    eleccion=randint(1,num_profesiones)
    profesion=Profesion.objects.get(numero=eleccion)
    return profesion

def crea_usuario_random(idUsuario):
    edad_random=randint(1,100)
    genero_random=choice(["F","M"])
    equipo_random=elige_equipo_random()
    profesion_random=elige_profesion_random()
    zip_code_random=randint(10000,90000)
    usuario=Usuario(numUsuario=idUsuario,edad=edad_random,genero=genero_random,equipo_favorito=equipo_random,profesion=profesion_random,zipCode=zip_code_random)
    return usuario

def populateUsuarios():
    print("Cargando usuarios...")
    usuarios=NUM_USUARIOS
    usuarios_a_crear=[]
    dict_usuarios={}
    for idUsuario in range(usuarios): #Para cada usuario
        idUsuario+=1
        usuario_aleatorio=crea_usuario_random(idUsuario)
        usuarios_a_crear.append(usuario_aleatorio)
        dict_usuarios[idUsuario]=usuario_aleatorio
    Usuario.objects.bulk_create(usuarios_a_crear)
    print("Usuarios insertadas: " + str(Usuario.objects.count()))
    print("---------------------------------------------------------")
    return dict_usuarios

def split_lista_jugadores(lista,chunks):
    lista_splitted_numpy=np.array_split(np.array(lista),chunks)
    lista_splitted=[]
    for numpy_array in lista_splitted_numpy:
        lista_splitted.append(numpy_array.tolist())
    return lista_splitted

def populatePuntuaciones():
    print("Cargando puntuaciones...")
    jugadores_valiosos=list(Jugador.objects.all().order_by("-valor",).filter(valor__gt=20)) #Jugadores con valor mayor a 20 millones
    if len(jugadores_valiosos)<30:
        return redirect('/error')
    chunks=4
    weights=(50, 25, 15, 10)#Probalidad de elegir uno de los 4 trozos de la lista de jugadores
    chunks_lista_jugadores=split_lista_jugadores(jugadores_valiosos,chunks)
    votos_min_por_usuario=VOTOS_POR_USUARIO[0]
    votos_max_por_usuario=VOTOS_POR_USUARIO[1]
    usuarios=NUM_USUARIOS
    puntuaciones_a_crear=[]
    for idUsuario in range(usuarios): #Para cada usuario
        idUsuario+=1
        num_votaciones=randint(votos_min_por_usuario,votos_max_por_usuario) #¿Cuantas votaciones va a hacer?
        usuario_actual=Usuario.objects.get(numUsuario=idUsuario)
        for _ in range(num_votaciones):
            chunk_jugadores=choices(range(chunks), weights=weights, k=1)[0] #Elige una de las 4 partes de la lista de jugadores
            posibles_jugadores=chunks_lista_jugadores[chunk_jugadores]
            jugador_aleatorio=choice(posibles_jugadores)
            
            if chunk_jugadores==0 or chunk_jugadores==1: #Si pertenece a los dos mejores trozos de jugadores
                if usuario_actual.equipo_favorito == jugador_aleatorio.equipo: #Si es de su equipo favorito
                    rating_elegido=choices([4,5],k=1)
                else:
                    rating_elegido=choices([3,4,5],k=1)
            else:
                if usuario_actual.equipo_favorito == jugador_aleatorio.equipo:
                    rating_elegido=choices([3,4],k=1)
                else:
                    rating_elegido=choices([1,2,3],k=1)
            puntuacion=Puntuacion(usuario=usuario_actual,jugador=jugador_aleatorio,rating=rating_elegido[0])
            puntuaciones_a_crear.append(puntuacion)
    Puntuacion.objects.bulk_create(puntuaciones_a_crear)
    print("Puntuaciones insertadas: " + str(Puntuacion.objects.count()))
    print("---------------------------------------------------------")
        
    
def populateProfesiones():
    print("Cargando profesiones...")
    lista=[]
    fileobj=open(path+"\\u.profesiones", "r")
    for line in fileobj.readlines():
        split=line.split(" ")
        lista.append(Profesion(numero=int(split[0].strip()),nombre=str(split[1].strip())))
    fileobj.close()
    Profesion.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    print("Profesiones insertadas: " + str(Profesion.objects.count()))
    print("---------------------------------------------------------")
    
def populate_RS():
    borra_datos_anteriores()
    populateProfesiones()
    u=populateUsuarios()
    return populatePuntuaciones()
