# Asistente de voz por comandos

Aplicación en Python que escucha instrucciones en lenguaje natural (o las lee por teclado), las valida con una gramática formal y ejecuta acciones concretas: buscar o reproducir contenido en la web, abrir programas en Windows y responder por voz sintética.

Está pensada como **base modular**: puedes ampliar verbos, reglas gramaticales y acciones editando unos pocos archivos, sin reescribir todo el flujo.

---

## ¿Qué es y para qué sirve?

Es un **asistente por comandos** con palabra de activación (por ejemplo “Alexa …”, “Google …”). Tras la activación, reconoce un **verbo** (`reproduce`, `busca`, `abre`, etc.) y el **resto de la frase** se usa como argumento (búsqueda en YouTube/Google o nombre de aplicación).

Sirve para:

- Automatizar tareas habituales con la voz (o con texto en modo depuración).
- Experimentar con **reconocimiento de voz**, **síntesis de voz** y **procesamiento del lenguaje natural ligero** (gramática) en un solo proyecto pequeño.
- Partir de un código ordenado si quieres integrar más servicios o reglas propias.

---

## Cómo funciona (visión general)

El flujo sigue el esquema clásico **percibir → interpretar → actuar**:

1. **Percibir**: se captura audio del micrófono (o se escribe un comando en consola) y se obtiene texto mediante reconocimiento automático del habla.
2. **Interpretar**: el texto se normaliza (minúsculas, sin acentos), se divide en palabras (*tokens*) y se comprueba si la secuencia encaja en una **gramática** definida en el código. Así se evita ejecutar frases mal formadas.
3. **Actuar**: si la frase es válida, según el verbo se llama a funciones que abren el navegador, lanzan un `.exe` o generan mensajes de voz.

La voz de respuesta confirma lo que va a hacer el sistema y guía al usuario si falta información (por ejemplo, no se dijo qué buscar).

---

## Tecnologías y piezas del proyecto

### Reconocimiento de voz (entrada de audio)

- **Librerías**: [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) captura audio con **PyAudio** y, en esta configuración, envía el audio al **reconocimiento en la nube de Google** (`recognize_google`), que devuelve texto. Requiere **conexión a Internet**.
- **Idioma**: por defecto `es-MX`; se puede cambiar con variable de entorno o en `asistente_voz/config.py` (`LANGUAGE_STT`). Códigos típicos: `es-ES`, `es-MX`, `en-US`, etc. (los que soporte el proveedor).
- **Micrófono**: el índice del dispositivo se configura en `config.py` (comentarios en ese archivo explican cómo listar micrófonos con un comando de Python). También puedes fijar `ASISTENTE_MIC_INDEX` sin tocar el código.

### Gramática (validación de la frase)

- **Librería**: [NLTK](https://www.nltk.org/) con una **gramática libre de contexto (CFG)** escrita como texto en `asistente_voz/gramatica.py`.
- **Idea**: las órdenes válidas tienen una estructura fija, por ejemplo *palabra de activación* + *verbo* + *complemento*. La CFG describe patrones como “Alexa reproduce …” o “Google abre el notepad”.
- **Consultas abiertas** (canción, término de búsqueda): no se listan todas las frases posibles en la gramática; para verbos como `reproduce` o `busca`, la cola de palabras se sustituye internamente por un comodín (`__objeto__`) y el analizador solo comprueba que haya “algo” después del verbo. Para `abre`, los nombres de aplicación sí van como reglas concretas en la gramática (alineadas con `acciones.py` y `config.py`).

### Síntesis de voz (respuesta hablada)

- **En Windows**: por defecto se intenta usar **SAPI** a través de `win32com` (habitualmente instalado con el paquete **pywin32**). Si no está disponible, se usa **pyttsx3** con el motor `sapi5`.
- **En otros sistemas**: pyttsx3 con el motor que tenga disponible el SO.
- **Parámetros**: velocidad y volumen se ajustan en `config.py` o con variables de entorno (`ASISTENTE_TTS_RATE`, `ASISTENTE_TTS_VOLUME`). Ver comentarios en `asistente_voz/voz_tts.py` para forzar solo pyttsx3 o preferir voz en español.

### Acciones (efectos en el equipo y la web)

- **Librerías**: [pywhatkit](https://pypi.org/project/pywhatkit/) para abrir búsquedas o reproducción en el navegador; **webbrowser** y **subprocess** como respaldo o para lanzar ejecutables (Bloc de notas, Word, Edge, etc.).
- Las rutas de aplicaciones en Windows están centralizadas en `config.py` para que puedas adaptarlas a tu instalación.

### Normalización de texto

- En `asistente_voz/texto.py` se unifica el formato del texto reconocido para que coincida con las palabras de la gramática y se corrige el orden si el motor de reconocimiento devuelve primero el verbo y después la palabra de activación.

---

## Requisitos

- **Sistema operativo**: probado y orientado a **Windows** (rutas de Edge/Office y TTS por SAPI). Con cambios menores en rutas y dependencias puede adaptarse a Linux o macOS.
- **Python**: 3.10 o superior recomendado.
- **Hardware**: micrófono si usas modo voz.
- **Red**: obligatoria para el reconocimiento con Google en la configuración actual.

---

## Entorno virtual (recomendado)

Aislar las dependencias en un entorno virtual (`.venv`) evita conflictos con otros proyectos y deja claro qué paquetes usa este código.

### Crear el entorno (Windows, PowerShell)

Desde la carpeta raíz del repositorio (donde está `requirements.txt`):

```powershell
python -m venv .venv
```

### Activar el entorno

**PowerShell** (si aparece error de política de ejecución, puede hacer falta `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` una vez):

```powershell
.\.venv\Scripts\Activate.ps1
```

**Símbolo del sistema (cmd)**:

```bat
.\.venv\Scripts\activate.bat
```

Tras activar, el prompt suele mostrar `(.venv)` al inicio.

### Instalar dependencias dentro del entorno

Con el entorno **activado**:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Eso instala lo declarado en `requirements.txt` (entre otros: `nltk`, `SpeechRecognition`, `pyaudio`, `pyttsx3`, `pywhatkit`).

**Si falla la instalación de PyAudio en Windows**, es un caso frecuente; suele resolverse con ruedas precompiladas o herramientas como `pipwin` (indicaciones en comentarios al inicio de `requirements.txt`).

### Opcional: voz SAPI con `win32com` en Windows

Para que el programa use primero **SAPI por COM** (comportamiento por defecto en Windows en `voz_tts.py`), instala también:

```powershell
pip install pywin32
```

Si no está instalado, el código sigue funcionando usando **pyttsx3**.

---

## Cómo ejecutar el proyecto

La carpeta raíz debe ser la del repositorio (donde está `Asistente_Voz_IA.py`), con el entorno virtual activado y dependencias instaladas.

### Arranque principal

```powershell
python Asistente_Voz_IA.py
```

### Arranque alternativo (desde la misma raíz)

```powershell
python scripts/ejecutar_asistente.py
```

Ese script añade la raíz al `PYTHONPATH` y llama al mismo punto de entrada; es útil si prefieres tener el comando bajo `scripts/`.

### Modo solo texto (sin micrófono)

Útil en entornos ruidosos, sin permisos de micrófono o para depurar la gramática y las acciones:

**PowerShell**

```powershell
$env:ASISTENTE_TEXTO = "1"
python Asistente_Voz_IA.py
```

**cmd**

```bat
set ASISTENTE_TEXTO=1
python Asistente_Voz_IA.py
```

En modo texto escribes el comando cuando aparezca `Comando >`. La misma gramática y las mismas acciones se aplican que en modo voz.

---

## Ejemplos de comandos

La frase debe incluir una **palabra de activación** al inicio (tras la normalización): `alexa`, `siri`, `google` o `cortana`. Luego un **verbo** reconocido y el resto según la acción.

- `alexa reproduce luis miguel`
- `siri busca tutorial python`
- `google abre el notepad`
- `cortana abre edge`

Los verbos y las palabras de activación deben estar alineados entre `asistente_voz/gramatica.py` y `asistente_voz/config.py`.

---

## Configuración

### Archivo `asistente_voz/config.py`

Ahí se concentran:

- **Lista de palabras de activación y verbos** (`WAKE_WORDS`, `VERBOS`): deben coincidir con la CFG en `gramatica.py`.
- **Idioma del reconocimiento**, tiempos de escucha, calibración de ruido, límites de duración de frase.
- **Volumen y velocidad del TTS**.
- **Índice del micrófono** y comentarios con el comando para listar dispositivos.
- **Rutas** a ejecutables (Edge, Word, Bloc de notas) y etiquetas amigables para la voz.

En el propio archivo hay comentarios en español que explican bloque por bloque qué tocar y para qué sirve cada valor.

### Variables de entorno (opcional)

Muchas claves tienen un valor por defecto en código; las variables permiten probar sin editar archivos. Algunas de las más útiles:

| Variable | Efecto |
|----------|--------|
| `ASISTENTE_TEXTO` | `1` activa modo consola en lugar del micrófono. |
| `ASISTENTE_MIC_INDEX` | Número de dispositivo de entrada; anula el índice por defecto de `config.py`. |
| `ASISTENTE_LISTAR_MICS` | `1` lista todos los micrófonos al iniciar (para elegir índice). |
| `ASISTENTE_LANG_STT` | Idioma del reconocimiento (p. ej. `es-MX`, `es-ES`). |
| `ASISTENTE_ESCUCHA_TIMEOUT` | Segundos de espera a que empieces a hablar. |
| `ASISTENTE_FRASE_MAX_S` | Duración máxima capturada por comando (0 = sin tope). |
| `ASISTENTE_TTS_RATE` / `ASISTENTE_TTS_VOLUME` | Ritmo y volumen del habla. |
| `ASISTENTE_TTS_PYTTSX3` | `1` fuerza motor pyttsx3 en Windows en lugar de SAPI/COM. |
| `ASISTENTE_TTS_VOZ_ES` | `1` intenta seleccionar una voz en español si existe. |
| `ASISTENTE_DEBUG_STT` | `1` imprime información extra del reconocimiento. |
| `ASISTENTE_REPETIR_STT_VOZ` | `1` hace que el asistente repita por voz lo que entendió (útil para depurar). |

La lista completa de ajustes finos está documentada con comentarios en `config.py`, `voz_stt.py` y `voz_tts.py`.

---

## Estructura del repositorio

```
Asistente_Voz/
├── asistente_voz/           # Código del asistente (paquete Python)
│   ├── agente.py            # Bucle principal: escucha/lee, valida, despacha acciones
│   ├── config.py            # Parámetros y rutas (mic, STT, TTS, verbos, aplicaciones)
│   ├── gramatica.py         # CFG NLTK y comprobación de validez de la frase
│   ├── texto.py             # Normalización de texto y orden de tokens
│   ├── voz_stt.py           # Micrófono + reconocimiento (SpeechRecognition / Google)
│   ├── voz_tts.py           # Síntesis de voz (SAPI / pyttsx3)
│   └── acciones.py          # YouTube, Google, apertura de programas
├── requirements.txt
├── README.md
├── Asistente_Voz_IA.py      # Punto de entrada recomendado
└── Base_Hechos.py               # Sistema experto por rasgos (animales); independiente del asistente de voz
```

Para **ampliar** el asistente suele bastar con:

1. Añadir reglas y vocabulario en `gramatica.py` y los mismos tokens en `VERBOS` / `WAKE_WORDS` en `config.py`.
2. Implementar la lógica nueva en `acciones.py` (o en otro módulo tuyo) y enlazar el verbo en `agente.py` dentro de `procesar_comando`.

---

## Privacidad y uso del micrófono

El audio del micrófono se envía al proveedor de reconocimiento configurado (Google en el código actual) para obtener texto. No sustituye leer la documentación oficial de ese servicio sobre retención y términos de uso. En modo `ASISTENTE_TEXTO=1` no se usa el micrófono para los comandos.

---

## Resolución rápida de problemas

| Síntoma | Qué revisar |
|---------|-------------|
| No instala PyAudio | Ruedas para tu versión de Python/Windows o `pipwin` (ver `requirements.txt`). |
| No escucha o escucha el mic equivocado | `ASISTENTE_LISTAR_MICS=1` y ajusta índice en `config.py` o `ASISTENTE_MIC_INDEX`. |
| Sin respuesta de voz en Windows | Instala `pywin32` o fuerza `ASISTENTE_TTS_PYTTSX3=1`. |
| “No entendió” o timeout | Ruido de fondo, `ASISTENTE_ESCUCHA_TIMEOUT`, `ASISTENTE_FRASE_MAX_S` o umbral de energía en `config.py`. |
| Gramática rechaza la frase | Orden de palabras, palabra de activación al inicio (tras normalización), verbo en `VERBOS` y reglas en `gramatica.py`. |


--------------------------------------------------------------------------------------------------------------

## Modificaciones del asistente de voz

- La los archivos modificados son:

Asistente_Voz/
├── asistente_voz/           
│   ├── agente.py            # Modificado
│   ├── config.py            # Modificado
│   ├── gramatica.py         # Modificado
│   ├── texto.py             
│   ├── voz_stt.py           
│   ├── voz_tts.py           
│   └── acciones.py          # Modificado
├── requirements.txt
├── README.md
├── Asistente_Voz_IA.py      
└── Base_Hechos.py           

- En el archivo config.py se modificaron las siguientes líneas:

WAKE_WORDS: frozenset[str] = frozenset({"andy"}) ← # Se cambio la palabra de activación a "andy".

VERBOS: frozenset[str] = frozenset(
    {
	"canta",
        "escribe",
        "reproduce",
        "reproducir",
        "busca",
        "buscar",
        "abre",
        "abrir",
        "inicia",       
        "wikipedia",     # ← NUEVO
        "wikipédia",     # ← NUEVO
        "wiki",          # ← NUEVO        
        "significa",     # ← NUEVO
        "significado",   # ← NUEVO
        "definición",    # ← NUEVO
        "define",        # ← NUEVO        
        "proximos",      # ← NUEVO
        "partidos",      # ← NUEVO
        "ultimos",       # ← NUEVO
        "resultados",    # ← NUEVO
    }
) ← # Se añadieron los verbos "wikipedia", "wikipédia", "wiki", "significa", "significado", "definición", "define", "proximos", "partidos", "ultimos", "resultados".

- En el archivo gramatica.py se modificaron las siguientes líneas:

GRAMATICA_TEXTO = r"""
S -> AV VP
AV -> 'andy' ← # Se cambio la palabra de activación a "andy".
VP -> V | V OBJ | V DET N | V N | V EN OBJ ← # Se agrego una acción para la búsqueda en Wikipedia.
DET -> 'el' | 'la' | 'los' | 'las' | 'al' | 'la'
EN -> 'en' ← # Se agrego una regla para la búsqueda en Wikipedia.
N -> 'perro' | 'gato' | 'luis' | 'miguel' | 'mana' | 'moderato' | 'jose'
N -> 'notepad' | 'word' | 'edge' | 'documento'
V -> 'canta' | 'escribe' | 'reproduce' | 'reproducir' | 'busca' | 'buscar' | 'abre' | 'abrir' | 'inicia' | 'wikipedia' | 'wikipédia' | 'wiki' | 'significa' | 'significado' | 'definición' | 'define' | 'proximos' | 'partidos' | 'ultimos' | 'resultados' ← # Se agregaron nuevos verbos "wikipedia", "wikipédia", "wiki", "significa", "significado", "definición", "define", "proximos", "partidos", "ultimos", "resultados". 
OBJ -> '__objeto__'
"""

VERBOS_CON_OBJETO_ABIERTO = frozenset({
    "reproduce", "reproducir",
    "busca", "buscar",
    "wikipedia", "wikipédia", "wiki",
    "significa", "significado", "definición", "define", 
    "proximos", "partidos", "ultimos", "resultados"
}) ← # Se agregaron nuevos verbos "wikipedia", "wikipédia", "wiki", "significa", "significado", "definición", "define", "proximos", "partidos", "ultimos", "resultados". 

- En el archivo acciones.py se modificaron las siguientes líneas:

Funciones
├── ejecutar_buscar_wikipedia
├── ejecutar_definir_palabra
├── ejecutar_proximos_partidos   
└── ejecutar_ultimos_resultados        

def ejecutar_buscar_wikipedia(consulta: str, hablar) -> None:
    """Busca en Wikipedia extrayendo inteligentemente el término de búsqueda."""
    import wikipediaapi # Biblioteca para consultar Wikipedia.
    import re # Importa expresiones regulares (para limpiar el texto).
    
    # Checamos que consulta no venga vacia.
    q_original = consulta.strip()
    if not q_original:
        hablar("Debes proporcionar un término.")
        return
    
    print(f"Consulta original: '{q_original}'")
    
    # Sebuscan posibles patrones comunes ya que solo se requiere el termino.
    patrones = [
        r'(?:sobre|acerca de|de|para|del)\s+(.+)$', 
        r'^(.+?)\s+(?:en wikipedia|wikipedia)$',     
        r'^(?:busca|buscar|búscame|consulta)\s+(.+)$', 
    ]
    
     # Comparamos cada patron con la cadena original, si  un patron coincide se guarda en q,  si ningun patron coincide q se queda en none.
    q = None
    for patron in patrones:
        match = re.search(patron, q_original, re.IGNORECASE) #Comparamos cada patron con la cadena original ingnorando mayusculas/minusculas
        if match:
            q = match.group(1).strip() # En caso de coincidencia guarda el grupo limpiando espacios al final y al principio y se sale del ciclo
            break
    
    # En caso de ho haber patrones se eliminan las palabras comunes ya que solo se requiere el termino.
    if not q:
        q = q_original
        palabras_eliminar = [
            "busca", "buscar", "búscame", "consulta", "consultar",
            "wikipedia", "wikipédia", "wiki", "sobre", "en", "de", 
            "la", "el", "los", "las", "para", "por"
        ] #Lista de palabras que se eliminarán de la consulta
        for palabra in palabras_eliminar:
            q = re.sub(r'\b' + palabra + r'\b', '', q, flags=re.IGNORECASE) # Con re.sub se substituye la palabre localizada por nada ('') sin importar que sean mayusculas/minusculas.
        q = re.sub(r'\s+', ' ', q).strip() # Substituimos los espacios en blanco que puedan existir en la frase por un solo espacio y se eliminan al final.
    
    if not q: # En cado de que q este vacio.
        hablar("No entendí qué quieres buscar. Di algo como 'andy wikipedia inteligencia artificial'")
        return
    
    print(f"Término extraído: '{q}'") # si q arrojo un resultado
    
    msg = f"Buscando {q} en Wikipedia." # se inicia la busqueda del termino.
    hablar(msg)
    
    # Se inicia la conexión a Whikipedia
    try:
        wiki_wiki = wikipediaapi.Wikipedia( # Se crea un cliente de Wikipedia
            language='es', # Busca en Wikipedia en español
            user_agent='MiAsistenteVoz/1.0' #  Identifica tu aplicación (requerido por Wikipedia)
        )
                
        for termino_prueba in [q, q.lower(), q.capitalize(), q.title()]: # Probar múltiples formas del término (Original, Todo minusculas, primera mayuscula, Cada palabra con mayusculas)
            page = wiki_wiki.page(termino_prueba) # Obtenemos la página
            if page.exists():
                resultado = page.summary[:500] # Tomamos los primeros 500 caracteres del resumen
                print(f"✅ Encontrado: {page.title}") # Imprime el resultado
                hablar(f"Según Wikipedia: {resultado}") # Lee el resultado en voz alta
                return
        
        # Si no se encuentra, sugerir búsqueda alternativa
        hablar(f"No encontré un artículo sobre {q}. Prueba con un término más corto o específico.")
        
    except Exception as e:
        print(f"Error: {e}")
        hablar("Tuve un problema consultando Wikipedia.")

def ejecutar_definir_palabra(consulta: str, hablar) -> None:
    """Busca definición usando diccionario local (100% confiable, sin internet)."""
    import re # Importa expresiones regulares (para limpiar el texto).
    
    # Diccionario local - puedes ampliarlo libremente
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
    
    palabra = consulta.strip().lower() # Elimina espacios al inicio y final y convierte todo a minúsculas
    if not palabra:
        hablar("Debes proporcionar una palabra")
        return
    
    # Limpiar la consulta (eliminar "define", "significa", etc.)
    palabra = re.sub(r'^(definición|significado|define|significa|qu[eé] es|qu[eé] significa)\s+', '', palabra)
    palabra = re.sub(r'\s+de\s+', ' ', palabra)
    palabra = palabra.strip()
    
    if not palabra:
        hablar("No entendí qué palabra quieres definir.")
        return
    
    print(f"📖 Buscando definición de: {palabra}")
    hablar(f"Buscando el significado de {palabra}...")
    
    # Normalizar sin acentos para búsqueda
    palabra_sin_acentos = palabra
    acentos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ü':'u'}
    for a, b in acentos.items():
        palabra_sin_acentos = palabra_sin_acentos.replace(a, b) # Obtenemos las palabras sin acentos
    
    # Buscar definición
    definicion = None
    
    if palabra in DICCIONARIO:
        definicion = DICCIONARIO[palabra] # Se buscan las palabras con acentos
    elif palabra_sin_acentos in DICCIONARIO:
        definicion = DICCIONARIO[palabra_sin_acentos] # Se buscan las palabras sin acentos
        print(f"🔍 Coincidencia encontrada: {palabra_sin_acentos}")
    
    if definicion:
        if len(definicion) > 500:
            definicion = definicion[:500] + "..." # Se encontro definicios, si es muy larga se leen los primero 500
        print(f"✅ Definición encontrada")
        hablar(definicion)
    else:
        hablar(f"No tengo definición para '{palabra}' en mi diccionario. Puedes ampliarlo editando el archivo.")

def ejecutar_proximos_partidos(consulta: str, hablar) -> None:
    """Solo próximos partidos de la Liga MX."""
    import urllib.request # Hacer peticiones HTTP a la API
    import json # Procesar la respuesta (convertir JSON a diccionario Python)
    import ssl # Configuración de seguridad para HTTPS
    
    print("📡 Consultando próximos partidos...")
    hablar("Consultando los próximos partidos de la Liga MX.")
    
    try:
        contexto = ssl._create_unverified_context() # Se usa SSL para seguridad de las conexiones HTTPS y _create_unverified_context() crea un tontexto que no verifica credenciales
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id=4350"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}) # urllib.request.Request() Crea las peticiones y con headers simulamos ser un avegador de internet
        
        with urllib.request.urlopen(req, timeout=15, context=contexto) as response: # Abrimos una conexion a la que le damos 15 segundos de espera y utilizamos el contexto generado anteriormente.
            data = json.loads(response.read().decode('utf-8')) # Leemos el reponse y lo convertimos a cadena de texto.
            eventos = data.get('events') # Otenemos la clave eventos
            
            if not eventos or len(eventos) == 0: # Validamos que la clave enventos existe o tenga valores
                hablar("No hay próximos partidos de la Liga MX en este momento.")
                return
            
            eventos = eventos[:3]  # Si esiste eventos se toman los primero 3 si hay muchos.
            mensaje = "Próximos partidos: "
            for evento in eventos: # Se leen las subclaves de la clave eventos, los cuales tienen un texto por default en caso de no tener valores
                local = evento.get('strHomeTeam', 'Local')
                visitante = evento.get('strAwayTeam', 'Visitante')
                fecha = evento.get('dateEvent', 'fecha por confirmar')
                hora = evento.get('strTime', 'hora por confirmar')
                
                if fecha and fecha != 'fecha por confirmar': # En caso de existir fecha la formateamos
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d') # De Y-M-D
                        fecha = fecha_obj.strftime('%d/%m') # A D/M
                    except:
                        pass
                
                mensaje += f"{local} vs {visitante} ({fecha} a las {hora}). "
            
            hablar(mensaje) # Se construye el mensaje y se lee en voz alta
            
    except Exception as e:
        print(f"Error: {e}")
        hablar("No pude consultar los próximos partidos.")


def ejecutar_ultimos_resultados(consulta: str, hablar) -> None:
    """Solo últimos resultados de la Liga MX."""
    import urllib.request # Hacer peticiones HTTP a la API
    import json # Procesar la respuesta (convertir JSON a diccionario Python)
    import ssl  # Configuración de seguridad para HTTPS
    
    print("📡 Consultando últimos resultados...")
    hablar("Consultando los últimos resultados de la Liga MX.")
    
    try:
        contexto = ssl._create_unverified_context() # Se usa SSL para seguridad de las conexiones HTTPS y _create_unverified_context() crea un tontexto que no verifica credenciales
        url = "https://www.thesportsdb.com/api/v1/json/3/eventspastleague.php?id=4350"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})  # urllib.request.Request() Crea las peticiones y con headers simulamos ser un avegador de internet
        
        with urllib.request.urlopen(req, timeout=15, context=contexto) as response: # Abrimos una conexion a la que le damos 15 segundos de espera y utilizamos el contexto generado anteriormente.
            data = json.loads(response.read().decode('utf-8')) # Leemos el reponse y lo convertimos a cadena de texto.
            eventos = data.get('events') # Otenemos la clave eventos
            
            if not eventos or len(eventos) == 0:
                hablar("No hay resultados recientes de la Liga MX.")
                return
                      
            eventos = eventos[:3] # Si esiste eventos se toman los primero 3 si hay muchos.
            mensaje = "Últimos resultados: "
            for evento in eventos: # Se leen las subclaves de la clave eventos, los cuales tienen un texto por default en caso de no tener valores
                local = evento.get('strHomeTeam', 'Local')
                visitante = evento.get('strAwayTeam', 'Visitante')
                goles_local = evento.get('intHomeScore', '?')
                goles_visitante = evento.get('intAwayScore', '?')
                fecha = evento.get('dateEvent', 'fecha desconocida')
                
                if fecha and fecha != 'fecha desconocida': # En caso de existir fecha la formateamos
                    try:
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d') # De Y-M-D
                        fecha = fecha_obj.strftime('%d/%m') # A D/M
                    except:
                        pass
                
                mensaje += f"{local} {goles_local} - {goles_visitante} {visitante} ({fecha}). "
            
            hablar(mensaje)  # Se construye el mensaje y se lee en voz alta
            
    except Exception as e:
        print(f"Error: {e}")
        hablar("No pude consultar los últimos resultados.")

- En el archivo agente.py se modificaron las siguientes líneas:

from asistente_voz.acciones import (
    detectar_alias_app_en_tokens,
    ejecutar_abrir_aplicacion,
    ejecutar_busqueda_google,
    ejecutar_reproducir_youtube,
    ejecutar_buscar_wikipedia,  # ← AÑADE ESTA LÍNEA
    ejecutar_definir_palabra,  # ← NUEVA IMPORTACIÓN
    ejecutar_proximos_partidos, # ← NUEVA IMPORTACIÓN
    ejecutar_ultimos_resultados, # ← NUEVA IMPORTACIÓN
) ← # Se importan las nuevas funciones generadas en acciones.py


 # NUEVO BLOQUE AQUÍ ↓
    if verbo in ("wikipedia", "wikipédia", "wiki"):
        ejecutar_buscar_wikipedia(" ".join(cola), hablar)
    # FIN DEL BLOQUE NUEVO
    # DICCIONARIO - Definir palabras
    elif verbo in ("significa", "significado", "definición", "define"):
        ejecutar_definir_palabra(" ".join(cola), hablar)
     # Fútbol - Próximos partidos
    elif verbo in ("proximos", "partidos"):
        ejecutar_proximos_partidos(" ".join(cola), hablar)
    # Fútbol - Últimos resultados
    elif verbo in ("ultimos", "resultados"):
        ejecutar_ultimos_resultados(" ".join(cola), hablar)  ← # Se asignan los verbos que se utilizaran para llamar a las funciones.

generador.generar_voz("Hasta luego Manuel Andrés.") ← # Se agrega mensaje de despedida.