# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto se adhiere a la [Semántica de Versiones](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-03-11

### Añadido
- **Auditoría y Compatibilidad con IA**: Refuerzo masivo del soporte para Agentes y LLMs.
- **API v1 Optimizada**: Nuevo esquema de herramientas (`/api/v1/tools_schema`) y endpoint de búsqueda (`/api/v1/search`) con limpieza agresiva de tokens y soporte nativo de idiomas.
- **Identidad Digital para Agentes**: Implementación de `robots.txt` y `ai.txt` en la raíz del servidor para facilitar el descubrimiento y uso por parte de asistentes de IA.
- **Paginación en Memoria**: El sistema ahora permite consultar "más resultados" desde el cache sin repetir la búsqueda real, ahorrando latencia y tokens de contexto.

### Corregido
- **Latencia de API**: Se han eliminado metadatos de UI innecesarios en las respuestas JSON, reduciendo el tamaño de la carga útil en un 50%.
- **Soporte de Idiomas en IA**: El endpoint de la herramienta ahora respeta el parámetro `language` enviado por el modelo.

## [1.2.0] - 2026-03-11

### Corregido
- **Error Crítico de Memoria y Recursos**: Se ha resuelto un problema grave que causaba el bloqueo del kernel (proceso de Python) y la ralentización total del sistema al ejecutarse en diferentes máquinas.
- **Fuga de Sockets e Hilos**: Reemplazada la creación de múltiples instancias de `AsyncClient` por un **Singleton Persistent Client** en `EngineManager`. Esto reduce drásticamente el overhead de hilos y sockets.
- **Fuga de Memoria en Cache**: Implementado un mecanismo de **Cache Pruning** (limpieza automática) que elimina entradas expiradas y limita el tamaño máximo del cache para evitar el consumo excesivo de RAM.
- **Estabilidad del Proxy**: Añadido límite de descarga de 10MB y timeouts estrictos en el endpoint `/proxify` para prevenir bloqueos de workers ante flujos de datos infinitos o abusivos.
- **Errores de Sintaxis**: Corregidos fallos de indentación en motores específicos (`wikidata.py`) introducidos durante el refactor de arquitectura.

### Añadido
- Inyección de dependencias del cliente compartido (`resp.client`) para todos los motores de búsqueda, permitiendo la reutilización efectiva del pool de conexiones HTTP/2.

---
*Nota: Este parche es obligatorio para asegurar la estabilidad del buscador en entornos locales de Windows.*
