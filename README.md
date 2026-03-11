# SearXena

SearXena es un metabuscador privado y local diseñado para proteger la identidad y privacidad de las búsquedas en internet, ofreciendo resultados consolidados de diversas fuentes sin rastreadores comerciales y reduciendo la huella digital.

## Características

* **Agregador Multinúcleo:** Obtiene resultados simultáneos y los clasifica desde motores como Google, Bing, DuckDuckGo, Brave, Wikipedia, entre otros.
* **Privacidad Primero:** Todas las peticiones son procesadas por tu nodo local, evitando perfilamiento por IPs o identificadores de cuenta.
* **Mapas con Privacidad Aislada:** Integración especial del visor de mapas interactivo de OpenStreetMap (Nominatim).
  * **Geocodificación Privada:** El análisis de las direcciones ocurre en el propio motor backend para garantizar que el historial textual no se filtre a la red OSM.
  * **Múltiples Coordenadas:** Capacidad de distinguir e indexar distintas geolocalizaciones homónimas limitadas de forma eficiente a la pestaña especializada ("Mapas").
  * **Visualizadores Estables:** Mantenimiento de una interfaz donde la tarjeta inteligente de ubicaciones coexiste interactivamente con links informacionales como Wikipedia sin estorbar los resultados generales de lectura.
* **Personalización CSS:** Diseños y layouts limpios e interactivos.

## Estructura de Mapas (Implementación OSM)

El subsistema "maps" que gestiona la búsqueda geográfica se encuentra implementado en `core/engines/osm.py`.
* Opera bajo la categoría delimitada `CATEGORIES = ['maps']` para asegurar que OSM no congestione las búsquedas textuales o documentales cotidianas.
* Cuenta con un bypass (`-1` score priority) en `core/engine_manager.py` cuando se visualiza dentro de su vista natural para proteger los resultados precisos contra el algoritmo estricto de string-matching que sirve para otros motores clásicos.
* Renderizado a través de `iframe` respetuoso a la fundación alojado en `templates/results.html`.

*Nota:* Ya que la interacción fluida arrastrable (zoom, paneo) carga _tiles_ oficiales de la web OpenStreetMap, la IP pública del consumidor emitirá una traza genérica estándar hacia OSM solo durante la fase visual. No se comparten palabras clave con terceros, garantizando privacidad contra rastreadores publicitarios corporativos.

---

*Proyecto de experimentación y soberanía local. Contribuciones bienvenidas.*
