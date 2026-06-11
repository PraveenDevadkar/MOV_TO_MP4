// Service Worker that injects COOP/COEP headers
// This enables SharedArrayBuffer on GitHub Pages

const CACHE = 'mov-mp4-v1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

self.addEventListener('fetch', function(event) {
  if (event.request.cache === 'only-if-cached' && event.request.mode !== 'same-origin') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(function(response) {
        const newHeaders = new Headers(response.headers);
        newHeaders.set('Cross-Origin-Embedder-Policy', 'require-corp');
        newHeaders.set('Cross-Origin-Opener-Policy',   'same-origin');

        return new Response(response.body, {
          status:     response.status,
          statusText: response.statusText,
          headers:    newHeaders,
        });
      })
      .catch(function() {
        return caches.match(event.request);
      })
  );
});
