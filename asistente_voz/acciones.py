"""YouTube, Google y programas (lo que hace el agente en el equipo)."""

from __future__ import annotations

# Cada función recibe la cola del comando (texto tras el verbo) y un callback hablar(msg) que usa el TTS.
# pywhatkit intenta abrir el navegador; si falla, se usa webbrowser como respaldo.
# Para nuevas apps en "abre", amplía resolver_ruta_aplicacion y ALIAS_ETIQUETA en config.py, y detectar_alias_app_en_tokens aquí.

import subprocess
import threading
import time
import webbrowser
import wikipediaapi

from urllib.parse import quote_plus

import pywhatkit

from asistente_voz.config import ALIAS_ETIQUETA, resolver_ruta_aplicacion


def _youtube_url(q: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(q)}"


def _google_url(q: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(q)}"


def _play_youtube_hilo(q: str) -> None:
    try:
        pywhatkit.playonyt(q)
    except Exception as e:
        print(f"[YouTube] {e} — abriendo búsqueda en el navegador.")
        webbrowser.open(_youtube_url(q))


def _buscar_google_hilo(q: str) -> None:
    try:
        pywhatkit.search(q)
    except Exception as e:
        print(f"[Google] pywhatkit: {e}")
        webbrowser.open(_google_url(q))


def ejecutar_reproducir_youtube(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres reproducir en YouTube.")
        return
    msg = f"Reproduciendo {q} en YouTube."
    print(msg)
    hablar(msg)
    time.sleep(0.7)
    threading.Thread(target=_play_youtube_hilo, args=(q,), daemon=True, name="yt").start()


def ejecutar_busqueda_google(consulta: str, hablar) -> None:
    q = consulta.strip()
    if not q:
        hablar("Di qué quieres buscar en Google.")
        return
    msg = f"Buscando {q} en Google."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    threading.Thread(target=_buscar_google_hilo, args=(q,), daemon=True, name="gg").start()


def ejecutar_abrir_aplicacion(alias: str, hablar) -> None:
    alias = alias.lower()
    ruta = resolver_ruta_aplicacion(alias)
    etiqueta = ALIAS_ETIQUETA.get(alias, alias)
    if ruta is None:
        hablar(f"No encontré instalada la aplicación {etiqueta}. Revisa config.py.")
        print(f"No hay ruta para: {alias}")
        return
    msg = f"Abriendo {etiqueta}."
    print(msg)
    hablar(msg)
    time.sleep(0.5)
    try:
        subprocess.Popen([str(ruta)], shell=False)
    except OSError as e:
        hablar("No pude lanzar la aplicación.")
        print(e)


def detectar_alias_app_en_tokens(tokens: list[str]) -> str | None:
    # Primera coincidencia con la lista; debe alinearse con lo que entiende resolver_ruta_aplicacion.
    apps = ("notepad", "word", "edge", "documento")
    found: str | None = None
    for t in tokens:
        if t in apps:
            found = t
    return found

def ejecutar_buscar_wikipedia(consulta: str, hablar) -> None:
    """Busca en Wikipedia extrayendo inteligentemente el término de búsqueda."""
    import wikipediaapi
    import re
        
    q_original = consulta.strip()
    if not q_original:
        hablar("Debes proporcionar un término.")
        return
    
    print(f"Consulta original: '{q_original}'")
    
    patrones = [
        r'(?:sobre|acerca de|de|para|del)\s+(.+)$', 
        r'^(.+?)\s+(?:en wikipedia|wikipedia)$',     
        r'^(?:busca|buscar|búscame|consulta)\s+(.+)$', 
    ]
        
    q = None
    for patron in patrones:
        match = re.search(patron, q_original, re.IGNORECASE)
        if match:
            q = match.group(1).strip()
            break
    
    if not q:
        q = q_original
        palabras_eliminar = [
            "busca", "buscar", "búscame", "consulta", "consultar",
            "wikipedia", "wikipédia", "wiki", "sobre", "en", "de", 
            "la", "el", "los", "las", "para", "por"
        ]
        for palabra in palabras_eliminar:
            q = re.sub(r'\b' + palabra + r'\b', '', q, flags=re.IGNORECASE)
        q = re.sub(r'\s+', ' ', q).strip()
    
    if not q:
        hablar("No entendí qué quieres buscar. Di algo como 'andy wikipedia inteligencia artificial'")
        return
    
    print(f"Término extraído: '{q}'")
    
    msg = f"Buscando {q} en Wikipedia."
    hablar(msg)
        
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            language='es',
            user_agent='MiAsistenteVoz/1.0'
        )
                
        for termino_prueba in [q, q.lower(), q.capitalize(), q.title()]:
            page = wiki_wiki.page(termino_prueba)
            if page.exists():
                resultado = page.summary[:500]
                print(f"OK... Encontrado: {page.title}")
                hablar(f"Según Wikipedia: {resultado}")
                return
                
        hablar(f"No encontré un artículo sobre {q}. Prueba con un término más corto o específico.")
        
    except Exception as e:
        print(f"Error: {e}")
        hablar("Tuve un problema consultando Wikipedia.")

def ejecutar_definir_palabra(consulta: str, hablar) -> None:
    """Busca definición usando diccionario local (100% confiable, sin internet)."""
    import re
        
    DICCIONARIO = {
        # Informática y tecnología
        "programacion": "La programación es el proceso de diseñar, codificar, depurar y mantener el código fuente de programas computacionales. Es el arte de dar instrucciones a una computadora.",
        "programación": "La programación es el proceso de diseñar, codificar, depurar y mantener el código fuente de programas computacionales. Es el arte de dar instrucciones a una computadora.",
        "algoritmo": "Conjunto ordenado y finito de operaciones que permite resolver un problema o realizar una tarea específica. Los algoritmos son la base de la programación.",
        "inteligencia": "Capacidad de entender, razonar, aprender de la experiencia, resolver problemas y adaptarse a nuevas situaciones.",
        "computadora": "Máquina electrónica que procesa datos y ejecuta instrucciones para realizar tareas diversas. También conocida como ordenador.",
        "internet": "Red global de computadoras interconectadas que utilizan el protocolo TCP/IP para comunicarse y compartir información.",
        "software": "Conjunto de programas, instrucciones y datos que hacen funcionar una computadora. Es la parte intangible del sistema.",
        "hardware": "Componentes físicos de una computadora o sistema electrónico: procesador, memoria, discos duros, teclado, pantalla, etc.",
        "aplicacion": "Programa informático diseñado para realizar una o varias funciones específicas para el usuario final.",
        "aplicación": "Programa informático diseñado para realizar una o varias funciones específicas para el usuario final.",
        "base de datos": "Conjunto de datos organizados y almacenados electrónicamente para su fácil acceso, gestión y actualización.",
        "red": "Conjunto de computadoras y dispositivos conectados entre sí para compartir información y recursos.",
        "python": "Lenguaje de programación de alto nivel, interpretado, de código abierto y muy popular en inteligencia artificial y ciencia de datos.",
        "javascript": "Lenguaje de programación usado principalmente para desarrollo web, que permite crear páginas interactivas y dinámicas.",
        
        # Ciencia
        "ciencia": "Conjunto de conocimientos obtenidos mediante la observación y el razonamiento, sistemáticamente estructurados.",
        "matematica": "Ciencia que estudia las propiedades de los números, las figuras geométricas y sus relaciones abstractas.",
        "matemáticas": "Ciencia que estudia las propiedades de los números, las figuras geométricas y sus relaciones abstractas.",
        "fisica": "Ciencia que estudia las propiedades de la materia, la energía, el espacio y el tiempo, así como sus interacciones.",
        "física": "Ciencia que estudia las propiedades de la materia, la energía, el espacio y el tiempo.",
        "quimica": "Ciencia que estudia la composición, estructura y propiedades de la materia y sus transformaciones.",
        "química": "Ciencia que estudia la composición, estructura y propiedades de la materia y sus transformaciones.",
        "biologia": "Ciencia que estudia los seres vivos, su origen, evolución, propiedades y procesos vitales.",
        "biología": "Ciencia que estudia los seres vivos, su origen, evolución, propiedades y procesos vitales.",
        
        # Filosofía y emociones
        "amor": "Sentimiento de afecto, cariño y apego hacia una persona, animal o cosa. Es una emoción fundamental en la experiencia humana.",
        "felicidad": "Estado de satisfacción, plenitud y bienestar emocional. Es un objetivo común en la vida de las personas.",
        "tristeza": "Emoción caracterizada por sentimientos de pérdida, desánimo, aflicción y falta de energía.",
        "conocimiento": "Familiaridad, comprensión o información adquirida a través de la experiencia, el estudio o el aprendizaje.",
        "sabiduria": "Capacidad de aplicar el conocimiento y la experiencia con inteligencia y buen juicio.",
        "sabiduría": "Capacidad de aplicar el conocimiento y la experiencia con inteligencia y buen juicio.",
        "verdad": "Correspondencia entre lo que se afirma y los hechos o la realidad.",
        "justicia": "Principio moral que busca la equidad, el respeto de los derechos y el bien común.",
        "libertad": "Capacidad y derecho de las personas para actuar según su propia voluntad, dentro de los límites de la ley.",
        
        # Educación y aprendizaje
        "aprender": "Adquirir conocimiento o habilidad a través del estudio, la experiencia o la enseñanza.",
        "enseñar": "Transmitir conocimientos, habilidades o valores a otra persona mediante métodos pedagógicos.",
        "estudiar": "Dedicar tiempo y atención a comprender y aprender un tema o materia.",
        "educacion": "Proceso de facilitar el aprendizaje de conocimientos, habilidades, valores y hábitos.",
        "educación": "Proceso de facilitar el aprendizaje de conocimientos, habilidades, valores y hábitos.",
    }
    
    palabra = consulta.strip().lower()
    if not palabra:
        hablar("Debes proporcionar una palabra")
        return
        
    palabra = re.sub(r'^(definición|significado|define|significa|qu[eé] es|qu[eé] significa)\s+', '', palabra)
    palabra = re.sub(r'\s+de\s+', ' ', palabra)
    palabra = palabra.strip()
    
    if not palabra:
        hablar("No entendí qué palabra quieres definir.")
        return
    
    print(f"Buscando definición de: {palabra}")
    hablar(f"Buscando el significado de {palabra}...")
        
    palabra_sin_acentos = palabra
    acentos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ü':'u'}
    for a, b in acentos.items():
        palabra_sin_acentos = palabra_sin_acentos.replace(a, b)
    
    # Buscar definición
    definicion = None
    
    if palabra in DICCIONARIO:
        definicion = DICCIONARIO[palabra]
    elif palabra_sin_acentos in DICCIONARIO:
        definicion = DICCIONARIO[palabra_sin_acentos]
        print(f"OK... Coincidencia encontrada: {palabra_sin_acentos}")
    
    if definicion:
        if len(definicion) > 500:
            definicion = definicion[:500] + "..."
        print(f"OK... Definición encontrada")
        hablar(definicion)
    else:
        hablar(f"No tengo definición para '{palabra}' en mi diccionario. Puedes ampliarlo editando el archivo.")

def ejecutar_proximos_partidos(consulta: str, hablar) -> None:
    """Solo próximos partidos de la Liga MX."""
    import urllib.request
    import json
    import ssl
    
    print("Consultando próximos partidos...")
    hablar("Consultando los próximos partidos de la Liga MX.")
    
    try:
        contexto = ssl._create_unverified_context()
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4350"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15, context=contexto) as response:
            data = json.loads(response.read().decode('utf-8'))
            eventos = data.get('events')
            
            if not eventos or len(eventos) == 0:
                hablar("No hay próximos partidos de la Liga MX en este momento.")
                return
            
            eventos = eventos[:3]
            mensaje = "Próximos partidos: "
            for evento in eventos:
                local = evento.get('strHomeTeam', 'Local')
                visitante = evento.get('strAwayTeam', 'Visitante')
                fecha = evento.get('dateEvent', 'fecha por confirmar')
                hora = evento.get('strTime', 'hora por confirmar')
                
                if fecha and fecha != 'fecha por confirmar':
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                        fecha = fecha_obj.strftime('%d/%m')
                    except:
                        pass
                
                mensaje += f"{local} vs {visitante} ({fecha} a las {hora}). "
            
            hablar(mensaje)
            
    except Exception as e:
        print(f"Error: {e}")
        hablar("No pude consultar los próximos partidos.")


def ejecutar_ultimos_resultados(consulta: str, hablar) -> None:
    """Solo últimos resultados de la Liga MX."""
    import urllib.request
    import json
    import ssl
    
    print("Consultando últimos resultados...")
    hablar("Consultando los últimos resultados de la Liga MX.")
    
    try:
        contexto = ssl._create_unverified_context()
        url = "https://www.thesportsdb.com/api/v1/json/3/eventspastleague.php?id=4350"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15, context=contexto) as response:
            data = json.loads(response.read().decode('utf-8'))
            eventos = data.get('events')
            
            if not eventos or len(eventos) == 0:
                hablar("No hay resultados recientes de la Liga MX.")
                return
                      
            eventos = eventos[:3]
            mensaje = "Últimos resultados: "
            for evento in eventos:
                local = evento.get('strHomeTeam', 'Local')
                visitante = evento.get('strAwayTeam', 'Visitante')
                goles_local = evento.get('intHomeScore', '?')
                goles_visitante = evento.get('intAwayScore', '?')
                fecha = evento.get('dateEvent', 'fecha desconocida')
                
                if fecha and fecha != 'fecha desconocida':
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                        fecha = fecha_obj.strftime('%d/%m')
                    except:
                        pass
                
                mensaje += f"{local} {goles_local} - {goles_visitante} {visitante} ({fecha}). "
            
            hablar(mensaje)
            
    except Exception as e:
        print(f"Error: {e}")
        hablar("No pude consultar los últimos resultados.")