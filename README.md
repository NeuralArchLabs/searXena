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
    <a href="#por-qué-no-tenemos-rival-en-windows">No Rival</a> • 
    <a href="#infraestructura-para-ia-sin-fricción">IA de Datos</a> • 
    <a href="#arquitectura-de-privacidad-transparente">Privacidad</a> • 
    <a href="#instalación-y-uso">Instalación</a> • 
    <a href="#licencia-y-créditos">Créditos</a>
  </p>
</div>

---

## 📖 Manifiesto: La Búsqueda "A la Antigua"

Internet ha cambiado. Lo que antes era una herramienta de descubrimiento, hoy es un ecosistema saturado de publicidad, algoritmos de recomendación forzados y rastreo persistente. **searXena** nace para devolverte el control.

Nuestra filosofía es recuperar la web de hace décadas: rápida, basada en texto relevante y libre de ruido. 
- **Sin Ruido:** Resultados directos, sin anuncios que distraigan o confundan.
- **Sin Perfiles:** No rastreamos tus búsquedas ni creamos historiales comerciales.
- **Soberanía Técnica:** Todo se ejecuta localmente en tu hardware, eliminando dependencias de nubes externas para tu curiosidad diaria.

## 🥊 ¿Por qué no tenemos rival en Windows?

Históricamente, los metabuscadores open-source enfocados en privacidad nacieron pensando en Linux. searXena rompe esa barrera siendo **100% nativo**.

| Característica | 👾 Los "Rivales" (Docker / WSL2) | 👑 searXena |
| :--- | :--- | :--- |
| **Arquitectura** | Virtualización Forzada | **Directa al Kernel** (Python nativo) |
| **Consumo de Memoria** | ~1 GB a 2 GB | **~30 MB - 60 MB** |
| **Tiempo de Arranque** | Lento (Inicia Docker Engine) | **Instantáneo** (Menos de 1 seg) |
| **Instalación** | Compleja (Comandos de sysadmin) | **Simple** (Scripts `.ps1` auto-setup) |
| **Tool Calling LLM** | Adaptadores externos requeridos | **API JSON Nativa** desde el día uno |

## 🤖 Infraestructura para IA sin Fricción

Para los desarrolladores de Inteligencia Artificial, searXena elimina los obstáculos de acceso a la web:

*   **Adiós a las API Keys:** Olvida la necesidad de gestionar múltiples llaves API o cuotas de suscripción. searXena es tu propio nodo de búsqueda infinito.
*   **Costo Cero por Consulta:** Escala tus agentes y sistemas RAG sin preocuparte por la factura.
*   **Datos de Grado Industrial:** Entrega un flujo de datos limpio y estructurado (JSON nativo) a través de nuestro motor de extracción propietario.

## ✨ Características Principales

* 🚀 **Metabúsqueda Paralela Asíncrona:** Una sola consulta dispara docenas de solicitudes asíncronas consolidándolas en menos de 1 segundo.
* 🧘 **O-ZEN Engine (Modo Lectura):** Motor de extracción industrial (AGPLv3) integrado para leer artículos y documentación técnica sin anuncios ni scripts intrusivos.
* 🛡️ **Privacidad Radical:** Centraliza las peticiones de forma transparente, protegiendo tu identidad ante la red global.
* 📱 **UI/UX Moderna:** Modo oscuro "Space Violet", interfaz responsiva y animaciones de alto nivel.

## 🔒 Arquitectura de Privacidad Transparente

### Proxificación del DOM Absoluta
Cuando buscas, searXena protege tu identidad a través de nuestro motor asíncrono. Toda URL de imagen devuelta pasa por nuestro sistema interno de `/proxify`, asegurando que tu IP no se exponga a servidores externos.

### Módulo de Mapas: OSM (OpenStreetMap)
- **Geocodificación Limpia**: Las peticiones de búsqueda van blindadas mediante el backend.
- **Transparencia IP**: Para interactividad (zoom/arrastre), inyectamos un `iframe` dinámico de `openstreetmap.org`. Esto causa una conexión directa temporal para la descarga de mosaicos visuales (tiles), lo cual es seguro al ser OSM una fundación pro-privacidad sin rastreadores comerciales.

### Aceleración de Activos de Confianza (Wikipedia/Wikimedia)
Identificamos servidores de alta confianza pública (Wikipedia) para carga directa de recursos multimedia, optimizando el rendimiento sin sacrificar la seguridad, ya que estas instituciones no utilizan telemetría publicitaria.

## 🚀 Instalación y Uso (Modo Local)

1.  **Clona el repositorio**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **Permisos de Script (Opcional)**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3.  **Instalador Automático**: Ejecuta `.\win_setup.ps1` en la terminal.
4.  **Iniciar**: Ejecuta `.\run.ps1` y abre `http://127.0.0.1:8000`.

## ⚖️ Licencia y Créditos

*   **Licencia:** searXena es software libre bajo la **GNU Affero General Public License v3.0 (AGPL-3.0)**.
*   **Créditos del Motor:** El motor de extracción **O-ZEN Engine** es una obra derivada que utiliza y adapta el núcleo de procesamiento de [Trafilatura](https://github.com/adbar/trafilatura) (Copyright Adrien Barbaresi), integrado aquí bajo AGPLv3 para garantizar la soberanía de datos del usuario.
*   **Agradecimientos:** Honramos la base técnica establecida por el ecosistema SearXNG, cuyos estándares de privacidad han inspirado esta arquitectura nativa.

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
