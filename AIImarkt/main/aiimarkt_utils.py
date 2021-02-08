from bs4 import BeautifulSoup
from main.models import Jugador, Equipo, Pais, PieChoice, PosicionPrincipal, PosicionSecundaria
import lxml
from datetime import datetime
import requests
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import re, os, shutil
from datetime import date

# HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
}
TRANSFERMARKT = "https://www.transfermarkt.es"
BASE_LEAGUE = "/main/marktwerteverein/wettbewerb/"
LALIGA = BASE_LEAGUE + "ES1"
PREMIER = BASE_LEAGUE + "GB1"
LIMITE_EQUIPOS = 20  # Hasta 20 normalmente


def bs_transfermarkt(url):
    pageTree = requests.get(url, headers=HEADERS, timeout=10060)
    s = BeautifulSoup(pageTree.text, "lxml")
    return s


def extraer_equipos():
    url = TRANSFERMARKT + LALIGA
    s = bs_transfermarkt(url)
    
    tabla_equipos = s.find("div", id="yw1").find("table", class_="items").tbody
    td_equipos = tabla_equipos.find_all("td", class_="hauptlink no-border-links", limit=LIMITE_EQUIPOS)

    lista_equipos = []
    for td in td_equipos:
        equipo = td.a.text
        enlace = TRANSFERMARKT + td.a["href"]
        lista_equipos.append({"equipo":equipo, "enlace":enlace})
    return lista_equipos


def extraer_jugadores(nombre_equipo, url_equipo):
    s = bs_transfermarkt(url_equipo)
    tabla_jugadores = s.find("div", id="yw1").find("table", class_="items").tbody
    td_jugadores = tabla_jugadores.find_all("td", class_="hauptlink")
    div_club = s.find("div", id="verein_head")
    div_escudo = div_club.find("div", class_="dataBild")
    escudo_url = div_escudo.find("img", alt=nombre_equipo)["src"]
    
    info_valor = s.find("div", class_="dataMarktwert")
    valor_equipo = extrae_valor(info_valor)

    lista_enlaces_jugadores = []
    for td in td_jugadores:
        span = td.find("span", class_="hide-for-small")
        if span != None:
            nombre = span.a.text
            enlace_jugador = TRANSFERMARKT + span.a["href"]
            if td.find("span", title="Capitán de equipo"):
                capitan = True
            else:
                capitan = False
            
            lista_enlaces_jugadores.append({"nombre":nombre, "enlace":enlace_jugador, "capitan":capitan})
    return lista_enlaces_jugadores, escudo_url, valor_equipo

    
def obtiene_posiciones(contents_posiciones, br):
    brs = [n for n, x in enumerate(contents_posiciones) if x == br]  # La posicion esta al lado de un <br>
    posiciones = []
    
    for index in brs:
        elemento_siguiente = contents_posiciones[index + 1].strip()
        posiciones.append(elemento_siguiente)
        
    return ",".join(posiciones)


def extrae_valor(div):
    valor = float(0)
    if div:
        info_valor = div.a.text.split("€")
        info_valor_splitted = info_valor[0].strip()
        cantidad = re.findall(r"[-+]?\d*\,\d+|\d+", info_valor_splitted)
        cantidad = cantidad[0].replace(",", ".")
        cantidad = float(cantidad)
    
        if not "mill" in info_valor_splitted:
            cantidad = cantidad / 1000
        if "mil mill" in info_valor_splitted:
            cantidad = cantidad * 1000
        valor = cantidad
    return valor
    
    
def extraer_datos_jugador(url_jugador, nombre):
    s = bs_transfermarkt(url_jugador)
    
    if not s.find("div", class_="dataMarktwert") or not s.find("div", class_="row collapse"):
        return
    
    # Valor
    info_valor = s.find("div", class_="dataMarktwert")
    valor = extrae_valor(info_valor)
    foto_url = s.find("div", class_="dataBild").find("img", alt=nombre)["src"]
    
    # Datos del jugador
    div_datos_jugador = s.find("div", class_="row collapse")

    tabla_ficha_jugador = div_datos_jugador.find("div", class_="spielerdaten").table
    edad = tabla_ficha_jugador.find("th", string="Edad:").find_next_sibling("td").get_text().strip()
    edad = int(edad)
    if tabla_ficha_jugador.find("th", string="Altura:"):
        altura_m = tabla_ficha_jugador.find("th", string="Altura:").find_next_sibling("td").get_text().strip()
        altura = re.findall(r"[-+]?\d*\,\d+|\d+", altura_m)
        altura = float(altura[0].replace(",", "."))
    else:
        altura = float(0.)
    
    if tabla_ficha_jugador.find("th", string="Pie:"):
        pie = tabla_ficha_jugador.find("th", string="Pie:").find_next_sibling("td").get_text().strip()
    else:
        pie = "indeterminado"
    td_nacionalidades = tabla_ficha_jugador.find("th", string="Nacionalidad:").find_next_sibling("td").find_all("img")
    nacionalidades_lista = []
    for img in td_nacionalidades:
        pais = img["alt"]
        nacionalidades_lista.append(pais)
    nacionalidades = ",".join(nacionalidades_lista)
    if tabla_ficha_jugador.find("th", string="Contrato hasta:").find_next_sibling("td").get_text().strip() == "-":
        contrato = datetime.strptime("30/06/2099", '%d/%m/%Y')
    else:
        contrato = datetime.strptime(tabla_ficha_jugador.find("th", string="Contrato hasta:").find_next_sibling("td").get_text().strip(), '%d/%m/%Y')

    # Datos de posicion
    if div_datos_jugador.find("div", class_="detailpositionen"):
        div_posiciones = div_datos_jugador.find("div", class_="detailpositionen").find("div", class_="auflistung")
        if div_posiciones.find("div", class_="hauptposition-left"):
            posicion_principal_contents = div_posiciones.find("div", class_="hauptposition-left").contents
        else:
            posicion_principal_contents = div_posiciones.find("div", class_="hauptposition-center").contents
        
        br = posicion_principal_contents[2]
        posicion_principal = obtiene_posiciones(posicion_principal_contents, br)
        if div_posiciones.find("div", class_="nebenpositionen"):
            posicion_secundaria_contents = div_posiciones.find("div", class_="nebenpositionen").contents
            posicion_secundaria = obtiene_posiciones(posicion_secundaria_contents, br)
        else:
            posicion_secundaria = "Ninguna"
    elif tabla_ficha_jugador.find("th", string=re.compile("Posici.n:")):
        posicion_principal = tabla_ficha_jugador.find("th", string=re.compile("Posici.n:")).find_next_sibling("td").get_text().strip()
        posicion_secundaria = "Ninguna"
    else:
        posicion_principal = "Ninguna"
        posicion_secundaria = "Ninguna"
    
    return edad, altura, nacionalidades, pie, posicion_principal, posicion_secundaria, valor, contrato, foto_url

    
def almacenar_datos_bs():
    equipos = extraer_equipos()
    lista_whoosh = []
    tablas = [Jugador, Equipo, Pais, PosicionPrincipal, PosicionSecundaria]
    for tabla in tablas:
        tabla.objects.all().delete()
    progreso = 1
    for eq in equipos:
        print("Analizando ", progreso, " de ", len(equipos), ' equipos')
        equipo = eq["equipo"]
        lista_jugadores, escudo_url, valor_equipo = extraer_jugadores(eq["equipo"], eq["enlace"])
        for jugador in lista_jugadores:
            nombre = jugador["nombre"]
            capitan = jugador["capitan"]
            
            try:
                edad, altura, nacionalidad, pie, posicion_principal, posicion_secundaria, valor, contrato, foto_jugador = extraer_datos_jugador(jugador["enlace"], nombre)
            except TypeError:
                continue
                        
            if pie == PieChoice.IZQ.value:
                pie_choice = PieChoice.IZQ
            elif pie == PieChoice.DER.value:
                pie_choice = PieChoice.DER
            elif pie == PieChoice.AMB.value:
                pie_choice = PieChoice.AMB
            elif pie == PieChoice.IND.value:
                pie_choice = PieChoice.IND
            
            equip, _ = Equipo.objects.get_or_create(nombre=equipo, valor=valor_equipo, url_escudo=escudo_url)
            
            pos_princ, _ = PosicionPrincipal.objects.get_or_create(nombre=posicion_principal)
            contr = date(contrato.year, contrato.month, contrato.day)

            jug = Jugador(nombre=nombre, edad=edad, altura=altura, valor=valor, contrato=contr, capitan=capitan, foto_jugador=foto_jugador, pie=pie_choice, posicion_principal=pos_princ, equipo=equip)
            jug.save()
            posicion_secundaria_split = posicion_secundaria.split(",")
            for p_s in posicion_secundaria_split:
                pos_sec, _ = PosicionSecundaria.objects.get_or_create(nombre=p_s)
                jug.posiciones_secundarias.add(pos_sec)
            paises_split = nacionalidad.split(",")
            for pais in paises_split:
                p, _ = Pais.objects.get_or_create(nombre=pais)
                jug.nacionalidades.add(p)
            
            lista_whoosh.append((nombre, edad, altura, nacionalidad, pie, posicion_principal, posicion_secundaria, valor, equipo, contrato))
        progreso += 1
    
    return lista_whoosh

    
def almacenar_datos():
        
    # define el esquema de la información
    schem = Schema(nombre=TEXT(stored=True), edad=NUMERIC(stored=True), altura=NUMERIC(stored=True), nacionalidad=KEYWORD(stored=True, commas=True),
                   pie=TEXT(stored=True), posicion_principal=KEYWORD(stored=True, commas=True), posicion_secundaria=KEYWORD(stored=True, commas=True), valor=NUMERIC(stored=True)
                   , equipo=TEXT(stored=True), contrato=DATETIME(stored=True))

    # eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    # creamos el índice
    ix = create_in("Index", schema=schem)
    # creamos un writer para poder añadir documentos al indice
    writer = ix.writer()
    i = 0
    lista = almacenar_datos_bs()
    for jugador in lista:
        # añade cada pelicula de la lista al índice
        writer.add_document(nombre=str(jugador[0]), edad=jugador[1], altura=float(jugador[2]), nacionalidad=str(jugador[3]), pie=str(jugador[4]),
                             posicion_principal=str(jugador[5]), posicion_secundaria=str(jugador[6]), valor=float(jugador[7]), equipo=str(jugador[8]), contrato=jugador[9])    
        i += 1
    writer.commit()
    print("Se han indexado " + str(i) + " jugadores")  


# WHOOSH
def buscar_posicion_valor(posicion, rango1, rango2):
    # abrimos el �ndice
    ix = open_dir("Index")

        # creamos un searcher en el �ndice    
    num_docs = ix.doc_count()
    jugadores = []
    with ix.searcher() as searcher:
            
        rango1 = str(rango1)
        rango2 = str(rango2)
        query_posicion = MultifieldParser(["posicion_principal", "posicion_secundaria"], ix.schema, group=OrGroup).parse("'" + posicion + "'")
        results_posicion = searcher.search(query_posicion, limit=num_docs, sortedby=["posicion_principal", "posicion_secundaria", "valor"], reverse=True)
        rango_valor = '[' + rango1 + ' TO ' + rango2 + ']'
        query_valor = QueryParser("valor", ix.schema).parse(rango_valor)
        results_valor = searcher.search(query_valor, limit=num_docs)
        if len(results_valor) == 0:
            return jugadores
        results_posicion.filter(results_valor)
        results = results_posicion
        
        for hit in results:
            nombre_hit = hit['nombre']
            valor_hit = hit['valor']
            jugador = Jugador.objects.get(nombre=nombre_hit, valor=valor_hit)
            jugadores.append(jugador)
            
    return  jugadores


def buscar_nacionalidad(en):
    # abrimos el �ndice
    ix = open_dir("Index")

    # creamos un searcher en el �ndice    
    num_docs = ix.doc_count()
    jugadores = []
    with ix.searcher() as searcher:
            
        query = QueryParser("nacionalidad", ix.schema).parse(en)
        results = searcher.search(query, limit=num_docs, sortedby=["valor"], reverse=True)
        
        for hit in results:
            nombre_hit = hit['nombre']
            valor_hit = hit['valor']
            jugador = Jugador.objects.get(nombre=nombre_hit, valor=valor_hit)
            jugadores.append(jugador)
                        
    return jugadores
    
    
def buscar_contrato(en):
    # abrimos el �ndice
    ix = open_dir("Index")

    # creamos un searcher en el �ndice    
    num_docs = ix.doc_count()
    jugadores = []
    with ix.searcher() as searcher:
        en_datetime = en.strftime("%Y%m%d")
 
        now = datetime.now()
        now_datetime = now.strftime("%Y%m%d")

        rango_fecha = '[' + now_datetime + ' TO ' + en_datetime + ']'
        query = QueryParser("contrato", ix.schema).parse(rango_fecha)
        results = searcher.search(query, limit=num_docs, sortedby=["contrato", "valor"], reverse=False)

        for hit in results:
            nombre_hit = hit['nombre']
            valor_hit = hit['valor']
            jugador = Jugador.objects.get(nombre=nombre_hit, valor=valor_hit)
            jugadores.append(jugador)
            
    return jugadores
    
    
def populate():
    almacenar_datos()

# DJANGO
def lista_posiciones_principales_secundarias():
    posiciones_principales = PosicionPrincipal.objects.values_list('nombre', flat=True)
    lista_posiciones_principales = list(posiciones_principales)
    posiciones_secundarias = PosicionSecundaria.objects.values_list('nombre', flat=True)
    lista_posiciones_secundarias = list(posiciones_secundarias)
    list_posiciones = lista_posiciones_principales + lista_posiciones_secundarias
    posiciones = list(dict.fromkeys(list_posiciones))
    if posiciones == []:
        return None
    posiciones.remove('Ninguna')
    posiciones_tuple = ()
    for pos in posiciones:
        tupla = (pos, pos,)
        posiciones_tuple = posiciones_tuple + (tupla,)   
    return posiciones_tuple


def lista_nacionalidades():
    nacionalidades = Pais.objects.values_list('nombre', flat=True)
    
    if nacionalidades == []:
        return None
    nacionalidades_tuple = ()
    for pais in nacionalidades:
        tupla = (pais, pais,)
        nacionalidades_tuple = nacionalidades_tuple + (tupla,)   
    return nacionalidades_tuple


def lista_equipos():
    equipos = Equipo.objects.values_list('nombre', flat=True)
    
    if equipos == []:
        return None
    equipos_tuple = ()
    for equipo in equipos:
        tupla = (equipo, equipo,)
        equipos_tuple = equipos_tuple + (tupla,)   
    return equipos_tuple
