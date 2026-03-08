# Acerca de searXena

searXena es un [metabuscador], que agrega los resultados de otros
{{link('motores de búsqueda', 'preferences')}} sin almacenar información sobre
sus usuarios.

El proyecto searXena es un fork centrado en la privacidad mantenido por NeuralArchLabs.
Únete a nosotros si tienes preguntas o solo quieres charlar.

Mejora searXena:

- Puedes mejorar las traducciones de searXena en [Weblate], o...
- Sigue el desarrollo, envía contribuciones e informa de problemas en [fuentes de searXena].
- Para obtener más información, visita la documentación del proyecto en [docs de
  searXena].

## ¿Por qué usarlo?

- searXena puede no ofrecerte resultados tan personalizados como Google, pero no
  genera un perfil sobre ti.
- searXena no se preocupa por lo que buscas, nunca comparte nada con terceros,
  y no puede usarse para comprometerte.
- searXena es software libre; el código es 100% abierto, y todos son bienvenidos
  a mejorarlo.

Si te importa la privacidad, quieres ser un usuario consciente, o crees en la
libertad digital, ¡haz de searXena tu motor de búsqueda predeterminado o
ejecútalo en tu propio servidor!

## ¿Cómo lo configuro como motor de búsqueda predeterminado?

searXena soporta [OpenSearch]. Para más información sobre cómo cambiar tu motor
de búsqueda predeterminado, consulta la documentación de tu navegador:

- [Firefox]
- [Microsoft Edge] - Tras el enlace, también encontrarás instrucciones útiles
  para Chrome y Safari.
- Los navegadores basados en [Chromium] solo añaden sitios web a los que el
  usuario navega sin una ruta.

Al añadir un motor de búsqueda, no debe haber duplicados con el mismo nombre.
Si encuentras un problema donde no puedes añadir el motor de búsqueda, puedes:

- Eliminar el duplicado (nombre por defecto: searXena) o
- Contactar al propietario para dar a la instancia un nombre diferente del predeterminado.

## ¿Cómo funciona?

searXena es un metabuscador mejorado para privacidad basado en SearXNG, que fue
inspirado por el [proyecto Seeks]. Proporciona privacidad básica mezclando tus
consultas con búsquedas en otras plataformas sin almacenar datos de búsqueda.
searXena puede añadirse a la barra de búsqueda de tu navegador; además, puede
configurarse como motor de búsqueda predeterminado.

La {{link('página de estadísticas', 'stats')}} contiene estadísticas útiles de uso
anónimo sobre los motores utilizados.

## ¿Cómo puedo tener mi propia instancia?

searXena agradece tu preocupación sobre los registros, así que toma el código de
las [fuentes de searXena] y ¡ejecútalo tú mismo!

Añade tu instancia para ayudar a otras personas a recuperar su privacidad y
hacer internet más libre. ¡Cuanto más descentralizado esté internet, más
libertad tendremos!


[fuentes de searXena]: {{GIT_URL}}
[docs de searXena]: {{get_setting('brand.docs_url')}}
[metabuscador]: https://es.wikipedia.org/wiki/Metabuscador
[Weblate]: https://translate.codeberg.org/projects/searxng/
[proyecto Seeks]: https://beniz.github.io/seeks/
[OpenSearch]: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
[Firefox]: https://support.mozilla.org/en-US/kb/add-or-remove-search-engine-firefox
[Microsoft Edge]: https://support.microsoft.com/en-us/help/4028574/microsoft-edge-change-the-default-search-engine
[Chromium]: https://www.chromium.org/tab-to-search