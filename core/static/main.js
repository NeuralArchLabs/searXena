/**
 * main.js - Lógica compartida para searXena Pro
 * Enfocado en privacidad local y rendimiento.
 */

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('search-input');
    const sbox = document.getElementById('suggestions-box');
    const form = document.getElementById('search-form');
    let timeout = null;

    if (input && sbox) {
        input.addEventListener('input', () => {
            clearTimeout(timeout);
            const q = input.value.trim();

            if (q.length < 2) {
                sbox.style.display = 'none';
                return;
            }

            timeout = setTimeout(async () => {
                try {
                    // La petición de sugerencias también pasa por nuestro backend
                    const r = await fetch(`/autoc?q=${encodeURIComponent(q)}`);
                    const data = await r.json();

                    if (data && data.length > 0) {
                        sbox.innerHTML = data.map(s =>
                            `<div class="suggestion-item" data-val="${s}">${s}</div>`
                        ).join('');
                        sbox.style.display = 'block';

                        // Delegación de eventos para las sugerencias
                        sbox.querySelectorAll('.suggestion-item').forEach(item => {
                            item.onclick = () => {
                                input.value = item.getAttribute('data-val');
                                form.submit();
                            };
                        });
                    } else {
                        sbox.style.display = 'none';
                    }
                } catch (e) {
                    sbox.style.display = 'none';
                }
            }, 250);
        });
    }

    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (sbox && !e.target.closest('.search-box') && !e.target.closest('.search-box-header')) {
            sbox.style.display = 'none';
        }
    });
});

/**
 * Cambia la categoría de búsqueda y reinicia la paginación
 */
function changeCat(cat) {
    const catInput = document.getElementById('cat-input');
    const pageInput = document.getElementById('page-input');
    const form = document.getElementById('search-form');

    if (catInput && form) {
        catInput.value = cat;
        if (pageInput) pageInput.value = 1;
        form.submit();
    }
}

/**
 * Navegación de páginas
 */
function goPage(p) {
    const pageInput = document.getElementById('page-input');
    const form = document.getElementById('search-form');

    if (pageInput && form) {
        pageInput.value = p;
        form.submit();
    }
}
