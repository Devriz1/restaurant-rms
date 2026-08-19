(function () {
    'use strict';

    let deferredPrompt = null;

    function showInstallBanner() {
        const banner = document.getElementById('pwaInstallBanner');
        if (banner) {
            banner.classList.add('show');
        }
    }

    function hideInstallBanner() {
        const banner = document.getElementById('pwaInstallBanner');
        if (banner) {
            banner.classList.remove('show');
        }
    }

    async function registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register('/serviceworker.js', {
                scope: '/',
            });

            console.log('ServiceWorker registered:', registration.scope);

            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                if (newWorker) {
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showInstallBanner();
                        }
                    });
                }
            });

            navigator.serviceWorker.addEventListener('controllerchange', () => {
                window.location.reload();
            });

        } catch (error) {
            console.error('ServiceWorker registration failed:', error);
        }
    }

    function setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            showInstallBanner();
        });

        window.addEventListener('appinstalled', () => {
            deferredPrompt = null;
            hideInstallBanner();
        });
    }

    function setupInstallButton() {
        const installBtn = document.getElementById('pwaInstallBtn');
        const dismissBtn = document.getElementById('pwaDismissBtn');

        if (installBtn) {
            installBtn.addEventListener('click', async () => {
                if (!deferredPrompt) return;

                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('Install prompt outcome:', outcome);
                deferredPrompt = null;
                hideInstallBanner();
            });
        }

        if (dismissBtn) {
            dismissBtn.addEventListener('click', hideInstallBanner);
        }
    }

    function setupOfflineStatus() {
        const onlineStatus = document.getElementById('onlineStatus');
        if (!onlineStatus) return;

        const updateStatus = () => {
            if (navigator.onLine) {
                onlineStatus.classList.remove('text-danger');
                onlineStatus.classList.add('text-success');
                onlineStatus.innerHTML = '<i class="bi bi-wifi me-1"></i> Online';
            } else {
                onlineStatus.classList.remove('text-success');
                onlineStatus.classList.add('text-danger');
                onlineStatus.innerHTML = '<i class="bi bi-wifi-off me-1"></i> Offline';
            }
        };

        window.addEventListener('online', updateStatus);
        window.addEventListener('offline', updateStatus);
        updateStatus();
    }

    document.addEventListener('DOMContentLoaded', function () {
        registerServiceWorker();
        setupInstallPrompt();
        setupInstallButton();
        setupOfflineStatus();
    });
})();
