(function () {
    'use strict';

    const CACHE_NAME = 'rms-v1';

    const STATIC_ASSETS = [
        '/',
        '/static/css/core/variables.css',
        '/static/css/core/layout.css',
        '/static/css/core/responsive.css',
        '/static/css/components/sidebar.css',
        '/static/css/components/navbar.css',
        '/static/css/components/buttons.css',
        '/static/css/components/forms.css',
        '/static/css/components/cards.css',
        '/static/css/components/tables.css',
        '/static/css/style.css',
        '/static/css/billing.css',
        '/static/css/billing_dashboard.css',
        '/static/css/orders.css',
        '/static/css/reports.css',
        '/static/css/report_customizer.css',
        '/static/js/app.js',
        '/static/js/pwa.js',
        '/static/js/waiter_pos.js',
        '/static/js/report_customizer.js',
        '/static/js/report_sort.js',
        '/static/js/report_search.js',
        '/static/manifest.json',
        '/static/icons/icon-192.png',
        '/static/icons/icon-512.png',
        '/static/icons/apple-touch-icon.png',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
        'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap',
    ];

    self.addEventListener('install', function (event) {
        event.waitUntil(
            caches.open(CACHE_NAME).then(function (cache) {
                return cache.addAll(STATIC_ASSETS);
            })
        );
        self.skipWaiting();
    });

    self.addEventListener('activate', function (event) {
        event.waitUntil(
            caches.keys().then(function (keys) {
                return Promise.all(
                    keys.filter(function (key) {
                        return key !== CACHE_NAME;
                    }).map(function (key) {
                        return caches.delete(key);
                    })
                );
            })
        );
        self.clients.claim();
    });

    self.addEventListener('fetch', function (event) {
        const request = event.request;

        if (request.method !== 'GET') {
            return;
        }

        const url = new URL(request.url);

        if (url.origin !== location.origin) {
            return;
        }

        event.respondWith(
            caches.match(request).then(function (cached) {
                const fetchPromise = fetch(request).then(function (networkResponse) {
                    if (networkResponse && networkResponse.status === 200) {
                        const clone = networkResponse.clone();
                        caches.open(CACHE_NAME).then(function (cache) {
                            cache.put(request, clone);
                        });
                    }
                    return networkResponse;
                }).catch(function () {
                    if (cached) {
                        return cached;
                    }
                    if (request.headers.get('accept').includes('text/html')) {
                        return caches.match('/offline/');
                    }
                });

                return cached || fetchPromise;
            })
        );
    });
})();
