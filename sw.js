/* 視聴リスト — オフライン用の Service Worker
 *
 * 画面と画像を端末に持っておき、通信がなくてもアプリを開けるようにする。
 * 作品の取り込みだけは外部サービスへの通信が要るので、そこは素通しにする。
 *
 * 画面を更新したら VERSION の数字を1つ増やすこと。
 * 古い保存分が捨てられ、新しい画面に入れ替わる。
 */
const VERSION = 'v1';
const CACHE = 'watchlist-' + VERSION;

// 最初にまとめて保存しておくもの
const ASSETS = [
  './',
  'index.html',
  'privacy.html',
  'site.webmanifest',
  'icon.svg',
  'apple-touch-icon.png',
  'icon-192.png',
  'icon-512.png',
  'icon-maskable-512.png',
  '視聴リスト_使い方ガイド.pdf'
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    // 1つ取れなくても残りは保存する（addAll は1つ失敗すると全部やり直しになる）
    await Promise.allSettled(ASSETS.map((a) => cache.add(new Request(a, { cache: 'reload' }))));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter((n) => n !== CACHE).map((n) => caches.delete(n)));
    await self.clients.claim();
  })());
});

async function networkFirst(request) {
  const cache = await caches.open(CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (e) {
    // 通信できないときは保存してある画面を出す
    return (await cache.match(request)) ||
           (await cache.match('index.html')) ||
           (await cache.match('./')) ||
           Response.error();
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(request);
  if (hit) {
    // 裏で最新版を取り直しておく（次回から新しくなる）
    fetch(request).then((fresh) => {
      if (fresh && fresh.ok) cache.put(request, fresh.clone());
    }).catch(() => {});
    return hit;
  }
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch (e) {
    return Response.error();
  }
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  // AniList・Wikipedia・Wikidata などへの通信には手を出さない
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req));      // 画面は更新を優先、駄目なら保存分
  } else {
    event.respondWith(cacheFirst(req));        // 画像などは保存分を優先
  }
});
