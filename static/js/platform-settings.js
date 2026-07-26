/**
 * Préférences plateforme SnapShop (localStorage).
 * N'affecte pas les vitrines boutique (shop_public).
 */
(function () {
    const STORAGE_KEY = "snapshop_platform_prefs_v1";

    const defaults = {
        themeMode: "light",
        reduceMotion: false,
    };

    const read = () => {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return { ...defaults };
            return { ...defaults, ...JSON.parse(raw) };
        } catch {
            return { ...defaults };
        }
    };

    const write = (prefs) => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
        } catch {
            /* quota */
        }
    };

    const resolveTheme = (mode) => {
        if (mode === "system") {
            return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
        }
        return mode === "dark" ? "dark" : "light";
    };

    const apply = (prefs) => {
        const resolved = resolveTheme(prefs.themeMode);
        document.documentElement.setAttribute("data-theme", resolved);
        document.documentElement.style.colorScheme = resolved;
        document.body.classList.toggle("snap-reduce-motion", !!prefs.reduceMotion);
        syncThemeButtons(prefs.themeMode);
    };

    const syncThemeButtons = (activeMode) => {
        document.querySelectorAll("[data-theme-choice]").forEach((btn) => {
            const on = btn.getAttribute("data-theme-choice") === activeMode;
            btn.classList.toggle("is-active", on);
            btn.setAttribute("aria-pressed", on ? "true" : "false");
        });
    };

    let prefs = read();
    apply(prefs);

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    media.addEventListener("change", () => {
        if (prefs.themeMode === "system") apply(prefs);
    });

    const panel = document.getElementById("platform-settings-panel");
    const overlay = document.getElementById("platform-settings-overlay");
    const openBtns = document.querySelectorAll("[data-open-platform-settings]");
    const closeBtn = document.getElementById("platform-settings-close");

    const setPanelOpen = (open) => {
        if (!panel || !overlay) return;
        panel.classList.toggle("hidden", !open);
        overlay.classList.toggle("hidden", !open);
        openBtns.forEach((b) => b.setAttribute("aria-expanded", open ? "true" : "false"));
        if (open) {
            const mobileMenu = document.getElementById("mobile-menu");
            const mobileOverlay = document.getElementById("mobile-menu-overlay");
            if (mobileMenu && !mobileMenu.classList.contains("hidden")) {
                mobileMenu.classList.add("hidden");
                mobileOverlay?.classList.add("hidden");
                document.getElementById("mobile-menu-button")?.setAttribute("aria-expanded", "false");
            }
            document.body.style.overflow = "hidden";
            closeBtn?.focus();
        } else {
            document.body.style.overflow = "";
        }
    };

    openBtns.forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const expanded = btn.getAttribute("aria-expanded") === "true";
            setPanelOpen(!expanded);
        });
    });

    closeBtn?.addEventListener("click", () => setPanelOpen(false));
    overlay?.addEventListener("click", () => setPanelOpen(false));

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && panel && !panel.classList.contains("hidden")) {
            setPanelOpen(false);
        }
    });

    document.querySelectorAll("[data-theme-choice]").forEach((btn) => {
        btn.addEventListener("click", () => {
            prefs.themeMode = btn.getAttribute("data-theme-choice") || "light";
            write(prefs);
            apply(prefs);
        });
    });

    const motionToggle = document.getElementById("pref-reduce-motion");
    if (motionToggle) {
        motionToggle.checked = !!prefs.reduceMotion;
        motionToggle.addEventListener("change", () => {
            prefs.reduceMotion = motionToggle.checked;
            write(prefs);
            apply(prefs);
        });
    }

    const clearCacheBtn = document.getElementById("pref-clear-catalog-cache");
    clearCacheBtn?.addEventListener("click", () => {
        try {
            sessionStorage.removeItem("snapshop_catalog_v1");
            clearCacheBtn.textContent = "Cache effacé ✓";
            window.setTimeout(() => {
                clearCacheBtn.textContent = "Effacer le cache catalogue";
            }, 2200);
        } catch {
            /* ignore */
        }
    });

    window.SnapShopPlatformPrefs = { read, write, apply };
})();
