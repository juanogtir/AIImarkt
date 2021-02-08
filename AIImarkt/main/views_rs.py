import shelve
from main.models import Jugador,Puntuacion, Usuario
from main.recommendations import  transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches
from django.shortcuts import render, get_object_or_404,redirect
from main.data_rs import populate_RS
from main.forms import UserForm,ItemForm
from django.conf import settings
from django.contrib.auth.decorators import login_required

def redirect_error(request):
    return render(request, 'error.html', {'STATIC_URL':settings.STATIC_URL})

@login_required(login_url='/ingresar')
def datos_RS(request):
    populate_RS()
    return redirect("/rs")

# Funcion que carga en el diccionario Prefs todas las puntuaciones de usuarios a peliculas. Tambien carga el diccionario inverso
# Serializa los resultados en dataRS.dat
def loadDict():
    Prefs={}   # matriz de usuarios y puntuaciones a cada a items
    shelf = shelve.open("dataRS.dat")
    puntuaciones = Puntuacion.objects.all()
    for punt in puntuaciones:
        idJugador = int(punt.jugador.idJugador)
        idUsuario = int(punt.usuario.id)
        rating = float(punt.rating)
        Prefs.setdefault(idUsuario, {})
        Prefs[idUsuario][idJugador] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=5)
    shelf.close()
    

@login_required(login_url='/ingresar')
def loadRS(request):
    loadDict()
    return render(request,'loadRS.html')

def recomendarJugadoresUsuario(request):
    items=None
    idUsuario=None
    usuario=None
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            idUsuario = form.cleaned_data['id']
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            shelf.close()
            try:
                usuario=Usuario.objects.get(id=int(idUsuario))
            except:
                return redirect('/error')
            puntuaciones = getRecommendations(Prefs,int(idUsuario))
            recommended = puntuaciones[:3]
            jugadores = []
            scores = []
            for re in recommended:
                jugadores.append(Jugador.objects.get(pk=re[1]))
                scores.append(re[0])
            items= zip(jugadores,scores)
    return render(request,'searchRecommendJugadores.html', {'user': usuario, 'items': items,'form': form})

def recomendarJugadoresItem(request):
    items=None
    idUsuario=None
    usuario=None
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            idUsuario = form.cleaned_data['id']
            shelf = shelve.open("dataRS.dat")
            Prefs = shelf['Prefs']
            SimItems = shelf['SimItems']
            shelf.close()
            try:
                usuario=Usuario.objects.get(id=int(idUsuario))
            except:
                return redirect('/error')
            rankings = getRecommendedItems(Prefs, SimItems, int(idUsuario))
            recommended = rankings[:3]
            jugadores = []
            scores = []
            for re in recommended:
                jugadores.append(Jugador.objects.get(pk=re[1]))
                scores.append(re[0])
            items= zip(jugadores,scores)
    return render(request,'searchRecommendJugadores.html', {'user': usuario, 'items': items,'form': form})

def jugadoresSimilares(request):
    items=None
    jugador=None
    form = ItemForm()
    if request.method=='POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            idJugador = form.cleaned_data['id']
            jugador = get_object_or_404(Jugador, pk=idJugador)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            try:
                ItemsPrefs[int(idJugador)]
            except KeyError:
                return redirect('/error')
            recommended = topMatches(ItemsPrefs, int(idJugador),n=5)
            jugadores = []
            similar = []
            for re in recommended:
                jugadores.append(Jugador.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(jugadores,similar)
    return render(request,'searchSimilarJugadores.html', {'form': form,'jugador': jugador,'items': items})

def recomendarUsuariosAJugadores(request):
    items=None
    jugador=None
    form = ItemForm()
    if request.method=='POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            idJugador = form.cleaned_data['id']
            jugador = get_object_or_404(Jugador, pk=idJugador)
            shelf = shelve.open("dataRS.dat")
            ItemsPrefs = shelf['ItemsPrefs']
            shelf.close()
            try:
                ItemsPrefs[int(idJugador)]
            except KeyError:
                return redirect('/error')
            rankings = getRecommendations(ItemsPrefs,int(idJugador))
            recommended = rankings[:3]
            usuarios = []
            similar = []
            for re in recommended:
                usuarios.append(Usuario.objects.get(pk=re[1]))
                similar.append(re[0])
            items= zip(usuarios,similar)
    return render(request,'searchRecommendUsuarios.html', {'form': form,'jugador': jugador,'items': items})
    
    