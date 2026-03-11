/**
 * main.js - Lógica compartida para searXena
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
 * Single Page App Navigation & Caching (Avoid redundant API requests)
 */
const CACHE_PREFIX = 'sxq_';

// Handle Browser Back/Forward buttons
window.addEventListener('popstate', (e) => {
    if (e.state && e.state.url) {
        performSearch(e.state.url, false);
    } else {
        window.location.reload();
    }
});

// Intercept main search form to clear cache on NEW searches
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            // Clear old cache for new queries manually if needed, or simply let it fetch.
            // On a new text query, it's fine to just do standard submit, 
            // but we can also handle it via SPA:
            e.preventDefault();
            const url = getSearchUrl();
            performSearch(url, true, true);
        });
    }
});

function getSearchUrl() {
    const q = document.getElementById('search-input')?.value.trim() || '';
    const cat = document.getElementById('cat-input')?.value || 'general';
    const page = document.getElementById('page-input')?.value || 1;
    return `/search?q=${encodeURIComponent(q)}&category=${cat}&pageno=${page}`;
}

async function performSearch(url, pushState = true, isNewQuery = false) {
    const layout = document.querySelector('.results-page-layout');

    // Only intercept if we are already on the results page
    if (!layout) {
        window.location.href = url;
        return;
    }

    if (layout) layout.style.opacity = '0.4';

    try {
        let htmlContent = null;

        // Check SessionStorage Cache (Only if it's not a fresh new text query)
        if (!isNewQuery) {
            htmlContent = sessionStorage.getItem(CACHE_PREFIX + url);
        }

        if (!htmlContent) {
            const resp = await fetch(url);
            const text = await resp.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');
            const newLayout = doc.querySelector('.results-page-layout');

            if (newLayout) {
                htmlContent = newLayout.innerHTML;
                // Save to cache to avoid refetches when returning to tab
                try {
                    sessionStorage.setItem(CACHE_PREFIX + url, htmlContent);
                } catch (e) {
                    sessionStorage.clear(); // Free up space if full
                    sessionStorage.setItem(CACHE_PREFIX + url, htmlContent);
                }
            } else {
                window.location.href = url; // Fallback
                return;
            }
        }

        if (layout) {
            layout.innerHTML = htmlContent;
            layout.style.opacity = '1';
        }

        if (pushState) {
            window.history.pushState({ url: url }, '', url);
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        window.location.href = url; // Fallback
    }
}

/**
 * Cambia la categoría de búsqueda y usa SPA Cache
 */
function changeCat(cat) {
    const catInput = document.getElementById('cat-input');
    const pageInput = document.getElementById('page-input');

    if (catInput) {
        catInput.value = cat;
        if (pageInput) pageInput.value = 1;
        performSearch(getSearchUrl(), true, false);
    }
}

/**
 * Navegación de páginas con SPA Cache
 */
function goPage(p) {
    const pageInput = document.getElementById('page-input');

    if (pageInput) {
        pageInput.value = p;
        performSearch(getSearchUrl(), true, false);
    }
}
