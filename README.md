<div align="center">
  <p>
    <a href="README.en.md">English</a> | 🌎 <b>Versión en Español</b> | <a href="README.zh.md">中文</a>
  </p>

  <img src="https://img.shields.io/badge/Sear-Xena-6a00ff?style=for-the-badge&logo=search&logoColor=white" alt="searXena Logo"/>
  <h1>searXena</h1>

  <p>
    <b>Search locally, search privately, search the old way.</b>
  </p>
  
  <p>
    Un metabuscador nativo y una infraestructura de datos de alto rendimiento creada para recuperar la web útil. Diseñado para humanos que buscan relevancia sin anuncios y para agentes de IA que necesitan explorar internet sin las complicaciones de las llaves API comerciales y sus costos asociados.
  </p>
  
  <p>
    <a href="#manifiesto-la-búsqueda-a-la-antigua">Manifiesto</a> • 
    <a href="#infraestructura-para-ia-sin-fricción">IA de Datos</a> • 
    <a href="#características-principales">Características</a> • 
    <a href="#arquitectura-de-privacidad">Privacidad</a> • 
    <a href="#instalación-y-uso">Instalación</a> • 
    <a href="#licencia-y-créditos">Créditos</a>
  </p>
</div>

---

## 📖 Manifiesto: La Búsqueda "A la Antigua"

Internet ha cambiado. Lo que antes era una herramienta de descubrimiento, hoy es un ecosistema saturado de publicidad, algoritmos de recomendación forzados y rastreo persistente. **searXena** nace para devolverte el control.

Nuestra filosofía es simple: la web debe ser rápida, relevante y privada. 
- **Sin Ruido:** Resultados directos, sin anuncios que distraigan o confundan.
- **Sin Perfiles:** No rastreamos tus búsquedas ni creamos historiales comerciales.
- **Soberanía Técnica:** Todo se ejecuta localmente en tu hardware, eliminando dependencias de nubes externas para tu curiosidad diaria.

## 🤖 Infraestructura para IA sin Fricción

Para los desarrolladores de Inteligencia Artificial, el acceso a la web en tiempo real suele ser una odisea de gestión. **searXena rompe las barreras tradicionales**:

*   **Adiós a las API Keys:** Olvida la necesidad de gestionar múltiples llaves API, cuotas de suscripción dinámicas o el agotamiento de créditos por cada consulta. searXena es tu propio nodo de búsqueda infinito.
*   **Costo Cero por Consulta:** Escala tus agentes y sistemas RAG (*Retrieval-Augmented Generation*) sin preocuparte por la factura al final del mes. 
*   **Datos de Grado Industrial:** Entrega un flujo de datos limpio y estructurado (JSON nativo) diseñado para ser procesado por modelos de lenguaje, eliminando el ruido visual y el overhead de los navegadores tradicionales.

## ✨ Características Principales

* 🚀 **Metabúsqueda Paralela Asíncrona:** Una sola consulta dispara docenas de solicitudes asíncronas de forma coordinada, consolidando los mejores resultados globales en menos de 1 segundo.
* 🧘 **O-ZEN Engine (Modo Lectura):** Motor de extracción industrial (AGPLv3) integrado para leer artículos y documentación técnica en una interfaz pura, eliminando scripts intrusivos y elementos de distracción.
* 🤖 **Integración IA-First:** Esquemas de "Tool Calling" pre-construidos para conectar tus LLMs a la web de forma instantánea.
* 📱 **UI/UX Moderna y Dinámica:** Animaciones fluidas, modo oscuro "Space Violet" y una interfaz responsiva diseñada para la máxima productividad.
* 🛡️ **Privacidad Radical:** Centraliza las peticiones de forma transparente, actuando como una interfaz neutral que protege tu identidad ante la red global.

## 🛠️ Stack Tecnológico

searXena aprovecha tecnologías modernas para una ejecución hiperfluida en hardware local:
- **Backend:** Python y FastAPI (Asíncrono de alto rendimiento).
- **Extracción:** `O-ZEN Engine` (Núcleo de extracción nativo optimizado).
- **Procesamiento:** `httpx` para peticiones paralelas HTTP/2 de bajísima latencia.
- **Frontend:** Jinja2 con Vanilla JavaScript puro (cero frameworks pesados).

## 🚀 Instalación y Uso

1.  **Clona el repositorio**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **Configura el entorno**: Ejecuta `.\win_setup.ps1` (Windows).
3.  **Inicia el motor**: Ejecuta `.\run.ps1`.
4.  Abre `http://127.0.0.1:8000` y vuelve a buscar de verdad.

## ⚖️ Licencia y Créditos

*   **Licencia:** searXena es software libre bajo la **GNU Affero General Public License v3.0 (AGPL-3.0)**.
*   **Créditos del Motor:** El motor de extracción **O-ZEN Engine** es una obra derivada que utiliza y adapta el núcleo de procesamiento de Trafilatura (Copyright Adrien Barbaresi), integrado aquí bajo AGPLv3 para garantizar la soberanía de datos del usuario y el cumplimiento del copyleft profesional.
*   **Agradecimientos:** Reconocemos la base teórica y técnica establecida por el ecosistema SearXNG, cuyos estándares de privacidad han inspirado la arquitectura de searXena.

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
