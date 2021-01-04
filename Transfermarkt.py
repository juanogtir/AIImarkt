from bs4 import BeautifulSoup

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import sqlite3
import lxml
from datetime import datetime
import requests
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, NUMERIC
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
import re, os, shutil


HEADERS = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
TRANSFERMARKT = "https://www.transfermarkt.es"
BASE_LEAGUE="/aii/marktwerteverein/wettbewerb/"
LALIGA = BASE_LEAGUE+"ES1"
LIMITE_EQUIPOS = 20  # Hasta 20


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Esta seguro que quiere recargar los datos. \nEsta operación puede ser lenta")
    if respuesta:
        almacenar_datos()


def bs_transfermarkt(url):
    pageTree = requests.get(url, headers=HEADERS)
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


def extraer_jugadores(nombre_equipo,url_equipo):
    s = bs_transfermarkt(url_equipo)
    tabla_jugadores = s.find("div", id="yw1").find("table", class_="items").tbody
    td_jugadores = tabla_jugadores.find_all("td", class_="hauptlink")
    div_club=s.find("div",id="verein_head")
    div_escudo=div_club.find("div",class_="dataBild")
    escudo_url=div_escudo.find("img",alt=nombre_equipo)["src"]
    
    info_valor = s.find("div", class_="dataMarktwert")
    valor_equipo = extrae_valor(info_valor)

    lista_enlaces_jugadores = []
    for td in td_jugadores:
        span = td.find("span", class_="hide-for-small")
        if span != None:
            nombre = span.a.text
            enlace_jugador = TRANSFERMARKT + span.a["href"]
            if td.find("span",title="Capitán de equipo"):
                capitan=True
            else:
                capitan=False
            
            lista_enlaces_jugadores.append({"nombre":nombre, "enlace":enlace_jugador, "capitan":capitan})
    return lista_enlaces_jugadores,escudo_url,valor_equipo

    
def obtiene_posiciones(contents_posiciones, br):
    brs = [n for n, x in enumerate(contents_posiciones) if x == br]  # La posicion esta al lado de un <br>
    posiciones = []
    
    for index in brs:
        elemento_siguiente = contents_posiciones[index + 1].strip()
        posiciones.append(elemento_siguiente)
        
    return ",".join(posiciones)

def extrae_valor(div):
    valor=float(0)
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
    
    
def extraer_datos_jugador(url_jugador):
    s = bs_transfermarkt(url_jugador)
    # Valor
    info_valor = s.find("div", class_="dataMarktwert")
    valor = extrae_valor(info_valor)
    
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
        altura=float(0.)
    
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
        contrato=datetime.strptime("30/06/2099", '%d/%m/%Y')
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
        posicion_principal=tabla_ficha_jugador.find("th", string=re.compile("Posici.n:")).find_next_sibling("td").get_text().strip()
        posicion_secundaria="Ninguna"
    else:
        posicion_principal="Ninguna"
        posicion_secundaria="Ninguna"
    
    return edad, altura, nacionalidades, pie, posicion_principal, posicion_secundaria, valor, contrato

    
def almacenar_datos_bs():
    
    conn = sqlite3.connect('jugadores.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS JUGADORES")
    conn.execute('''CREATE TABLE JUGADORES
       (NOMBRE TEXT NOT NULL,
        EDAD    INTEGER,
        ALTURA    REAL,
        NACIONALIDAD    TEXT,
        PIE    TEXT,
        PRINCIPAL    TEXT,
        SECUNDARIA    TEXT,
        VALOR    REAL,
        EQUIPO TEXT,
        CONTRATO DATE);''')

    equipos = extraer_equipos()
    lista_whoosh = []
    
    progreso = 1
    for eq in equipos:
        print("Analizando ", progreso, " de ", LIMITE_EQUIPOS)
        equipo = eq["equipo"]
        lista_jugadores,escudo_url,valor_equipo = extraer_jugadores(eq["equipo"],eq["enlace"])
        for jugador in lista_jugadores:
            nombre = jugador["nombre"]
            capitan=jugador["capitan"]

            edad, altura, nacionalidad, pie, posicion_principal, posicion_secundaria, valor, contrato = extraer_datos_jugador(jugador["enlace"])
            print(contrato,' ',contrato.year,contrato.month,contrato.day)
            conn.execute("""INSERT INTO JUGADORES (NOMBRE, EDAD, ALTURA,NACIONALIDAD,PIE,PRINCIPAL,SECUNDARIA,VALOR,EQUIPO,CONTRATO) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                         (nombre, edad, altura, nacionalidad, pie, posicion_principal, posicion_secundaria, valor, equipo, contrato))
            conn.commit()
            
            lista_whoosh.append((nombre, edad, altura, nacionalidad, pie, posicion_principal, posicion_secundaria, valor, equipo, contrato))
        progreso += 1
    cursor = conn.execute("SELECT COUNT(*) FROM JUGADORES")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()
    
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
    messagebox.showinfo("Fin de indexado", "Se han indexado " + str(i) + " jugadores")  
def jugador_to_string(r):
    return r['nombre']+' ('+str(r['edad'])+" - "+r['nacionalidad']+'): '+r['posicion_principal']+' ('+r['posicion_secundaria']+') | Valor:'+str(r['valor'])+' M, Club: '+r['equipo']+" ("+r['contrato'].strftime('%d/%m/%Y')+")"

def decode_list_utf8(lista):
    decoded_list=[]
    for i in lista:
        decoded_list.append(i.decode("utf-8"))
    return decoded_list

def buscar_posicion_valor():
    def mostrar_lista(event):
        #abrimos el �ndice
        ix=open_dir("Index")

        #creamos un searcher en el �ndice    
        num_docs=ix.doc_count()

        with ix.searcher() as searcher:

            posicion=entry_posicion.get()
            rango_valor=entry_rango.get()
            
            if not '-' in rango_valor:
                messagebox.showinfo("Error",
                        "La entrada " + rango_valor + " es incorrecta")
                entry_rango.delete(0, END)
                entry_rango.insert(0, '20-50')
                return
            
            rangos=rango_valor.split("-")
            rango1=rangos[0]
            rango2=rangos[1]
            query_posicion = MultifieldParser(["posicion_principal","posicion_secundaria"], ix.schema, group=OrGroup).parse("'"+posicion+"'")
            results_posicion = searcher.search(query_posicion,limit=num_docs,sortedby=["posicion_principal","posicion_secundaria","valor"],reverse=True)
            rango_valor = '['+ rango1 + ' TO ' + rango2 +']'
            query_valor = QueryParser("valor", ix.schema).parse(rango_valor)
            results_valor = searcher.search(query_valor,limit=num_docs)
            
            results_posicion.filter(results_valor)
            results=results_posicion
            num_resultados=len(results.docs())

            
            if num_resultados==0:
                messagebox.showinfo("Sin resultados",
                        "La entrada " + posicion+"|"+ rango1+"-"+rango2+ " no arrojó ningún resultado")
                return
            else:
                messagebox.showinfo("Resultados",
                        "Se han obtenido " + str(num_resultados) + " resultados")
            
            v = Toplevel()
            v.title("Listado de jugadores con valor entre "+str(rango1)+" y "+str(rango2)+" Millones")
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in results: 
                lb.insert(END,jugador_to_string(r))
                lb.insert(END, "-------------------------------------------------------------------------------------------------------")
    
    v = Toplevel()
    v.title("Busqueda por posición y rango de valor")
    v.geometry('500x50')
    l = Label(v, text="Introduzca Posicion|X-Y a buscar:")
    l.pack(side=LEFT)
    
    field_values_encoded1=open_dir("Index").searcher().lexicon("posicion_principal")
    field_values1=decode_list_utf8(field_values_encoded1)
    field_values_encoded2=open_dir("Index").searcher().lexicon("posicion_secundaria")
    field_values2=decode_list_utf8(field_values_encoded2)

    list_posiciones=field_values1+field_values2
    posiciones=list(dict.fromkeys(list_posiciones))
    posiciones.remove('Ninguna')
    
    entry_posicion = Spinbox(v, values=list(posiciones))
    entry_rango=Entry(v)
    entry_posicion.insert(END, 'Mediocentro')
    entry_rango.insert(END, '20-50')
    entry_posicion.bind("<Return>", mostrar_lista)
    entry_rango.bind("<Return>", mostrar_lista)
    entry_posicion.pack(side=LEFT)
    entry_rango.pack(side=LEFT)

def buscar_nacionalidad():
    def listar_nacionalidad(event):
        #abrimos el �ndice
        ix=open_dir("Index")

        #creamos un searcher en el �ndice    
        num_docs=ix.doc_count()
        
        with ix.searcher() as searcher:
            
            query = QueryParser("nacionalidad", ix.schema).parse(en.get())
            results = searcher.search(query,limit=num_docs,sortedby=["valor"],reverse=True)
            
            num_resultados=len(results.docs())
            
            messagebox.showinfo("Resultados",
                        "Se han obtenido " + str(num_resultados) + " resultados")
            
            v = Toplevel()
            v.title("Listado de jugadores de "+str(en.get()))
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in results: 
                lb.insert(END,jugador_to_string(r))
                lb.insert(END, "-------------------------------------------------------------------------------------------------------")
    
    v = Toplevel()
    v.title("Busqueda por nacionalidad")
    v.geometry('500x50')
    l = Label(v, text="Introduzca la nacionalidad a buscar:")
    l.pack(side=LEFT)
    
    field_values_encoded=open_dir("Index").searcher().lexicon("nacionalidad")
    field_values=decode_list_utf8(field_values_encoded)

    en = Spinbox(v, values=list(field_values))
    en.insert(END, 'España')
    en.bind("<Return>", listar_nacionalidad)
    en.pack(side=LEFT)
    
    
def buscar_contrato():
    def listar_contrato(event):
        #abrimos el �ndice
        ix=open_dir("Index")

        #creamos un searcher en el �ndice    
        num_docs=ix.doc_count()
        
        with ix.searcher() as searcher:
            try:
                en_datetime=datetime.strptime(en.get(), '%d/%m/%Y').strftime("%Y%m%d")
            except ValueError:
                messagebox.showinfo("Error", "Formato del rango de fecha incorrecto")
                en.delete(0, END)
                en.insert(END, '30/06/2021')
                return
            now = datetime.now()
            now_datetime=now.strftime("%Y%m%d")

            rango_fecha = '[' + now_datetime + ' TO ' + en_datetime + ']'
            query = QueryParser("contrato", ix.schema).parse(rango_fecha)
            results = searcher.search(query,limit=num_docs,sortedby=["contrato","valor"],reverse=False)
            
            num_resultados=len(results.docs())
            
            messagebox.showinfo("Resultados",
                        "Se han obtenido " + str(num_resultados) + " resultados")
            
            v = Toplevel()
            v.title("Listado de jugadores con contrato hasta "+str(en.get()))
            v.geometry('800x150')
            sc = Scrollbar(v)
            sc.pack(side=RIGHT, fill=Y)
            lb = Listbox(v, yscrollcommand=sc.set)
            lb.pack(side=BOTTOM, fill = BOTH)
            sc.config(command = lb.yview)
            for r in results: 
                lb.insert(END,jugador_to_string(r))
                lb.insert(END, "-------------------------------------------------------------------------------------------------------")
    
    v = Toplevel()
    v.title("Busqueda por contrato")
    v.geometry('500x50')
    l = Label(v, text="Introduzca la fecha de contrato a buscar:")
    l.pack(side=LEFT)
    
    en = Entry(v)
    en.insert(END, '30/06/2021')
    en.bind("<Return>", listar_contrato)
    en.pack(side=LEFT)
    
    
def ventana_principal():
    
    root = Tk()
    root.title("JUGADORES")
    menubar = Menu(root)
    
    # Datos
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    #Buscar
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Buscar por Posición", command=buscar_posicion_valor)
    buscarmenu.add_command(label="Buscar por Nacionalidad", command=buscar_nacionalidad)
    buscarmenu.add_command(label="Buscar por Contrato", command=buscar_contrato)
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
    
    root.config(menu=menubar)
    root.mainloop()
    

if __name__ == "__main__":
    ventana_principal()

