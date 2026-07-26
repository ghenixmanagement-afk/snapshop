"""Génération du thème visuel par boutique (preset + couleur de signature)."""
import re
from typing import Tuple

from .models import Shop

HEX_PATTERN = re.compile(r'^#?([0-9A-Fa-f]{6})$')
MAX_LOGO_BYTES = 5 * 1024 * 1024
ALLOWED_LOGO_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}

THEME_PRESETS = {
    'elegant': {
        'page_bg': '#0f172a',
        'surface': '#1e293b',
        'hero_from': '#1e293b',
        'hero_to': '#0f172a',
        'text': '#f8fafc',
        'muted': '#94a3b8',
        'border': '#334155',
        'catalog_bg': '#1e293b',
        'mode': 'dark',
    },
    'vif': {
        'page_bg': '#fff7ed',
        'surface': '#ffffff',
        'hero_from': '#ffedd5',
        'hero_to': '#ffffff',
        'text': '#1c1917',
        'muted': '#78716c',
        'border': '#fed7aa',
        'catalog_bg': '#fff7ed',
        'mode': 'light',
    },
    'nature': {
        'page_bg': '#f0fdf4',
        'surface': '#ffffff',
        'hero_from': '#dcfce7',
        'hero_to': '#ffffff',
        'text': '#14532d',
        'muted': '#4b5563',
        'border': '#bbf7d0',
        'catalog_bg': '#f0fdf4',
        'mode': 'light',
    },
    'modern': {
        'page_bg': '#eff6ff',
        'surface': '#ffffff',
        'hero_from': '#dbeafe',
        'hero_to': '#ffffff',
        'text': '#1e3a8a',
        'muted': '#64748b',
        'border': '#bfdbfe',
        'catalog_bg': '#eff6ff',
        'mode': 'light',
    },
    'classic': {
        'page_bg': '#faf9f7',
        'surface': '#ffffff',
        'hero_from': '#f5f5f4',
        'hero_to': '#ffffff',
        'text': '#1a1a1a',
        'muted': '#6b6560',
        'border': '#e8e4df',
        'catalog_bg': '#f5f5f4',
        'mode': 'light',
    },
}


def normalize_hex(value: str, default: str = '#1B3320') -> str:
    if not value:
        return default.upper()
    cleaned = value.strip()
    match = HEX_PATTERN.match(cleaned)
    if not match:
        return default.upper()
    return f'#{match.group(1).upper()}'


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = normalize_hex(hex_color).lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _channel(c: float) -> float:
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    rs, gs, bs = _channel(r / 255), _channel(g / 255), _channel(b / 255)
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs


def contrast_text_on(hex_color: str) -> str:
    return '#FFFFFF' if relative_luminance(hex_color) < 0.45 else '#1A1A1A'


def mix_hex(hex_a: str, hex_b: str, weight: float) -> str:
    """Mélange hex_a (weight=0) vers hex_b (weight=1)."""
    ar, ag, ab = hex_to_rgb(hex_a)
    br, bg, bb = hex_to_rgb(hex_b)
    w = max(0.0, min(1.0, weight))
    r = round(ar + (br - ar) * w)
    g = round(ag + (bg - ag) * w)
    b = round(ab + (bb - ab) * w)
    return f'#{r:02X}{g:02X}{b:02X}'


def build_shop_branding(shop: Shop) -> dict:
    preset = THEME_PRESETS.get(shop.theme, THEME_PRESETS['classic'])
    brand = normalize_hex(shop.custom_theme_color or '#1B3320')
    brand_light = mix_hex(brand, '#FFFFFF', 0.72)
    brand_soft = mix_hex(brand, '#FFFFFF', 0.88)
    brand_dark = mix_hex(brand, '#000000', 0.18)
    brand_text = contrast_text_on(brand)

    theme_labels = dict(Shop.THEME_CHOICES)
    logo_url = shop.logo.url if shop.logo else None

    css_vars = (
        f'--shop-brand:{brand};'
        f'--shop-brand-light:{brand_light};'
        f'--shop-brand-soft:{brand_soft};'
        f'--shop-brand-dark:{brand_dark};'
        f'--shop-brand-text:{brand_text};'
        f'--shop-page-bg:{preset["page_bg"]};'
        f'--shop-surface:{preset["surface"]};'
        f'--shop-hero-from:{preset["hero_from"]};'
        f'--shop-hero-to:{preset["hero_to"]};'
        f'--shop-text:{preset["text"]};'
        f'--shop-muted:{preset["muted"]};'
        f'--shop-border:{preset["border"]};'
        f'--shop-catalog-bg:{preset["catalog_bg"]};'
    )

    return {
        'theme': shop.theme,
        'theme_label': theme_labels.get(shop.theme, 'Classique'),
        'brand_color': brand,
        'brand_light': brand_light,
        'brand_soft': brand_soft,
        'brand_text': brand_text,
        'logo_url': logo_url,
        'mode': preset['mode'],
        'css_vars': css_vars,
        'theme_class': f'shop-vitrine shop-theme-{shop.theme}',
    }
