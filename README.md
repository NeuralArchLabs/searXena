<div align="center">
  <img src="https://img.shields.io/badge/Sear-Xena-6a00ff?style=for-the-badge&logo=search&logoColor=white" alt="SearXena Logo"/>
  <h1>SearXena</h1>

  <p>
    Un metabuscador ágil, local y 100% nativo para Windows enfocado en la privacidad extrema.
  </p>
  
  <p>
    <a href="#origen-y-agradecimientos">Origen</a> • 
    <a href="#stack-tecnológico">Stack</a> • 
    <a href="#características-principales">Características</a> • 
    <a href="#arquitectura-de-privacidad">Privacidad</a> • 
    <a href="#instalación-y-uso">Instalación</a> • 
    <a href="#licencia-y-créditos">Créditos</a>
  </p>
</div>

---

## 📖 Origen y Agradecimientos

SearXena nació originalmente como una iniciativa de investigación para realizar un *port* experimental de [SearXNG](https://github.com/searxng/searxng) destinado a ejecutarse de forma nativa en sistemas operativos Windows sin el peso de contenedores Docker o subsistemas WSL involucrados. 

A medida que el desarrollo avanzó y la necesidad de integraciones interactivas más profundas surgió, **SearXena evolucionó para convertirse en un software iterativamente independiente**. Nuestro código base fue reescrito y estructurado bajo una arquitectura de micro-gestores propia (FastAPI), conservando el espíritu de soberanía del usuario establecido por el movimiento open-source.

Reconocemos y honramos formalmente al proyecto original SearXNG y a sus desarrolladores comunitarios por sentar los estándares universales y la base teórica (parsers, evasión, headers proxy) acerca de cómo debe operar un metabuscador resistente a la censura.

## 🛠️ Stack Tecnológico

SearXena aprovecha tecnologías modernas y ultraligeras para permitir una ejecución hiperfluida inclusive en hardware de uso local secundario:

- **Backend:** [Python 3.x](https://www.python.org/) y [FastAPI](https://fastapi.tiangolo.com/) (Alto rendimiento asíncrono).
- **Servidor Web:** [Uvicorn](https://www.uvicorn.org/) (Soporte nativo ASGI).
- **Procesamiento de Red:** `httpx` para peticiones HTTP/2 paralelas y asíncronas de bajísima latencia.
- **Frontend / Rendering:** [Jinja2](https://jinja.palletsprojects.com/) acoplado con Vanilla JavaScript (cero frameworks tipo React) y CSS3 Puro garantizando velocidad instantánea.
- **Scraping Estructurado:** `lxml` y `BeautifulSoup4` acoplado con selectores modulares para el análisis del DOM.

## ✨ Características Principales

* 🚀 **Metabúsqueda Paralela Asíncrona:** Una sola consulta tuya dispara docenas de solicitudes asíncronas a motores globales (Google, Bing, DuckDuckGo, Brave, GitHub, Wikipedia, MDN, NPM, etc.) consolidándolas en menos de 1 segundo.
* 🛡️ **Burbuja de Privacidad Absoluta:** Actúa como un proxy intermediario entre tú y las mega-corporaciones. Ni Google ni Microsoft pueden perfilarte; todas las peticiones le llegan a ellos como originadas desde SearXena.
* 📦 **100% Nativo en Windows:** Cero dependencias complejas. Solo clona, instala las librerías con `pip`, corre el archivo `.py` principal y tienes un buscador corporativo evadiendo telemetría hospedado localmente en tu sistema.
* 📱 **UI/UX Moderna y Dinámica:** Animaciones fluidas, modo oscuro ultra refinado ("Space Violet"), interfaz responsiva y separada categóricamente en pestañas (General, TI/Ciencia, Mapas, Videos, Imágenes).
* 🌎 **Rich Snippets Consolidados:** Lectura enriquecida consolidando datos de Wikipedia o Wikidata en recuadros laterales de rápido consumo ("Infoboxes") al estilo de los grandes motores comerciales.

## 🔒 Arquitectura de Privacidad Transparente

SearXena prioriza que tus datos **jamás** terminen en perfiles publicitarios (Google/Meta), asumiendo un rol de escudo por debajo de la interfaz gráfica. Aún así, la arquitectura requiere ciertos consensos técnicos, reportados aquí transparentemente:

### Proxificación del DOM Absoluta
Cuando buscas cualquier consulta general (Noticias, TI, Código), SearXena enmascara tu identidad a través del motor asíncrono backend. Modificamos de forma sistemática los `User-Agent`. Toda URL de imagen devuelta por los motores comerciales pasa de manera forzada por nuestro sistema interno de `/proxify`, impidiendo que tu IP se filtre directamente.

### Módulo de Mapas: OSM (OpenStreetMap)
Al interactuar con la pestaña especializada de Mapas, SearXena implementa reglas un poco más permeables para lograr darte interactividad útil (arrastrar, hacer zoom), conservando el anonimato comercial:
* **Geocodificación Limpia**: La petición nominal (ej. "Buscar Jalisco") va blindada mediante el core backend a favor del anonimato. OSM jamás sabe las palabras de tu búsqueda.
* **Transparencia IP (El Iframe Interactivo)**: Para que experimentes un mapa funcional arrastrable dentro de la sección Mapas, inyectamos un `iframe` dinámico referenciando a `openstreetmap.org`. Esto hace que **tu navegador realice una conexión directa a OSM revelando temporalmente tu IP pública** para la descarga de mosaicos visuales (tiles).
* El trade-off: OSM es una fundación [abierta pro-privacidad](https://wiki.osmfoundation.org/wiki/Privacy_Policy) sin motores que subasten telemetría ni cookies inter-rastreo, por lo que la exposición de IP nativa es benigna y se justifica a cambio de integrar la cartografía funcional.

## 🚀 Instalación y Uso (Modo Local)

1. **Requisito Prevío:** Al menos Python 3.9 instalado en tu sistema.
2. Clona el repositorio a un directorio local:
   ```bash
   git clone https://github.com/martinezpalomera92/searXena.git
   cd searXena
   ```
3. (Opcional) Te recomendamos crear un entorno virtual para encapsular los paquetes:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. Instala todas las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
5. Inicia el motor SearXena:
   ```bash
   python app.py
   ```
Abre tu navegador (Brave, Edge, Firefox) y entra directamente en `http://127.0.0.1:8000`. SearXena ya está listo para enmascararte.

## ⚖️ Licencia y Créditos Restringidos

* Desarrollado independientemente por **Armando Martínez Palomera**.
* Todo el conocimiento de base técnica para modelar las clases de los módulos de extracción y derivaciones heurísticas, pertenecen de forma moral a los mantenedores pasados y presentes del formidable código de [Searx](https://github.com/searx/searx) (Iniciado por Taica) y [SearXNG](https://github.com/searxng/searxng).
* Herramientas de extracción comunitaria posibilitadas gracias a los estatus permisivos de entidades abiertas (como la familia Wikimedia Foundations).

*SearXena y todos sus recursos se emiten bajo fines de experimentación, soberanía digital individual y propósitos estrictamente educativos.*
