const CACHE_NAME = 'ups-podcast-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/style.css',
    '/static/css/home.css',
    '/static/js/script.js',
    '/static/js/videos.js',
    '/static/images/logo.webp',
    '/static/images/header.webp'
];

// Instalar Service Worker y guardar en caché
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(ASSETS_TO_CACHE);
            })
    );
});

// Activar el Service Worker y limpiar cachés antiguos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Interceptar peticiones y devolver desde caché si está disponible
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Devuelve el recurso desde caché, de lo contrario lo pide a la red
                return response || fetch(event.request);
            })
    );
});
