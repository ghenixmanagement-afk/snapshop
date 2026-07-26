/**
 * Catalogue home: infinite scroll, sessionStorage cache, restauration scroll.
 * Cle sur actualisation (reload) ; conserve entre navigations (back / meme onglet).
 */
(function () {
    const STORAGE_KEY = "snapshop_catalog_v1";
    const grid = document.getElementById("catalog-products-grid");
    const sentinel = document.getElementById("catalog-sentinel");
    const statusEl = document.getElementById("catalog-load-status");
    const feedUrl = document.getElementById("catalog-feed-config")?.dataset.feedUrl;
    const pageSize = 12;

    if (!grid || !sentinel || !feedUrl) return;

    const searchParams = () => window.location.search || "";
    const cacheKey = () => `${window.location.pathname}${searchParams()}`;

    const isReload = () => {
        const nav = performance.getEntriesByType?.("navigation")?.[0];
        if (nav && nav.type === "reload") return true;
        if (performance.navigation && performance.navigation.type === 1) return true;
        return false;
    };

    const readCache = () => {
        try {
            const raw = sessionStorage.getItem(STORAGE_KEY);
            if (!raw) return null;
            return JSON.parse(raw);
        } catch {
            return null;
        }
    };

    const writeCache = (data) => {
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        } catch {
            /* quota / prive */
        }
    };

    const clearCache = () => {
        try {
            sessionStorage.removeItem(STORAGE_KEY);
        } catch {
            /* ignore */
        }
    };

    if (isReload()) {
        clearCache();
    }

    const renderCard = (p) => {
        const img = p.image_url
            ? `<div class="catalog-card__img-wrap"><img src="${escapeAttr(p.image_url)}" alt="${escapeAttr(p.name)}" loading="lazy"></div>`
            : `<div class="catalog-card__img-wrap flex items-center justify-center text-xs text-stone-400">Sans image</div>`;
        const detailBase = "/products/";
        const href = `${detailBase}${encodeURIComponent(p.slug)}/`;
        return `
<article class="card-ui p-3 flex flex-col" data-slug="${escapeAttr(p.slug)}">
  <a href="${href}" class="block flex-1">
    ${img}
    <p class="mt-3 text-xs text-stone-500">${escapeHtml(p.category)}</p>
    <h3 class="font-bold italic text-stone-900 line-clamp-2">${escapeHtml(p.name)}</h3>
    <p class="font-black mt-1 text-stone-900">${escapeHtml(p.price)} FCFA</p>
  </a>
  <a href="${href}" class="btn-secondary mt-3 w-full text-center text-xs">Voir le produit</a>
</article>`;
    };

    const escapeHtml = (s) =>
        String(s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    const escapeAttr = escapeHtml;

    let state = {
        items: [],
        nextOffset: 0,
        total: 0,
        hasMore: true,
        loading: false,
        urlKey: cacheKey(),
    };

    const setStatus = (text) => {
        if (statusEl) statusEl.textContent = text;
    };

    const appendProducts = (list) => {
        const frag = document.createDocumentFragment();
        const wrap = document.createElement("div");
        wrap.innerHTML = list.map(renderCard).join("");
        while (wrap.firstChild) frag.appendChild(wrap.firstChild);
        grid.appendChild(frag);
    };

    const fetchPage = async (offset) => {
        const u = new URL(feedUrl, window.location.origin);
        const params = new URLSearchParams(window.location.search);
        params.set("offset", String(offset));
        params.set("limit", String(pageSize));
        u.search = params.toString();
        const res = await fetch(u.toString(), {
            headers: { "X-Requested-With": "XMLHttpRequest", Accept: "application/json" },
            credentials: "same-origin",
        });
        if (!res.ok) throw new Error("Erreur reseau");
        return res.json();
    };

    const persist = () => {
        writeCache({
            urlKey: state.urlKey,
            items: state.items,
            nextOffset: state.nextOffset,
            total: state.total,
            hasMore: state.hasMore,
            scrollY: window.scrollY,
        });
    };

    let scrollTimer;
    window.addEventListener(
        "scroll",
        () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(persist, 200);
        },
        { passive: true }
    );
    window.addEventListener("pagehide", persist);

    const restored = readCache();
    const canRestore =
        restored &&
        restored.urlKey === cacheKey() &&
        !isReload() &&
        Array.isArray(restored.items) &&
        restored.items.length > 0;

    const loadMore = async () => {
        if (state.loading || !state.hasMore) return;
        state.loading = true;
        setStatus("Chargement…");
        try {
            const data = await fetchPage(state.nextOffset);
            state.total = data.total;
            state.hasMore = !!data.has_more;
            state.nextOffset = data.next_offset;
            state.items = state.items.concat(data.products);
            appendProducts(data.products);
            persist();
            setStatus(
                state.hasMore
                    ? `Affichage de ${state.items.length} / ${state.total} produits — defilez pour en voir plus.`
                    : `${state.items.length} produit(s) au total.`
            );
        } catch (e) {
            setStatus("Impossible de charger la suite. Reessayez.");
        } finally {
            state.loading = false;
        }
    };

    const startObserver = () => {
        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((en) => {
                    if (en.isIntersecting) loadMore();
                });
            },
            { root: null, rootMargin: "200px", threshold: 0 }
        );
        io.observe(sentinel);
    };

    if (canRestore) {
        state.items = restored.items;
        state.nextOffset = restored.nextOffset;
        state.total = restored.total;
        state.hasMore = restored.hasMore;
        state.urlKey = restored.urlKey;
        appendProducts(restored.items);
        setStatus(
            state.hasMore
                ? `Affichage de ${state.items.length} / ${state.total} (cache) — defilez pour la suite.`
                : `${state.items.length} produit(s) au total.`
        );
        requestAnimationFrame(() => {
            window.scrollTo(0, typeof restored.scrollY === "number" ? restored.scrollY : 0);
        });
        startObserver();
        return;
    }

    state.nextOffset = 0;
    state.items = [];
    state.hasMore = true;
    loadMore().then(() => {
        startObserver();
    });
})();
