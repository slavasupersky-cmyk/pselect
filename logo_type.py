#!/usr/bin/env python3
"""
Логотип «Прохорова Select» заново — набором в шрифте, а не трассировкой.

Буквы берутся из шрифтовых файлов (fontTools → контуры глифов), расставляются по
пропорциям референса logo2.png и собираются в чистый SVG: знак P/S с диагональной
чертой, «ПРОХОРОВА», «SELECT», черта, «ЛЮДИ МЕСТА ВОЗМОЖНОСТИ». Кривые — настоящие
шрифтовые, без потерь. Цвета — классами lg-ink / lg-br (сайт красит под тему) и
автономные варианты со вшитыми цветами.

Шрифты (Google Fonts через npm @fontsource/*): дидоны с кириллицей — Prata,
Oranienbaum; гротеск для подписи — Manrope.
Запуск: python3 logo_type.py [prata|oranienbaum|cormorant]
"""
import sys, glob
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTS = Path('fonts')
def ff(name, subset, weight=400):
    return glob.glob(str(FONTS / f'fontsource-{name}-*/package/files/{name}-{subset}-{weight}-normal.woff'))[0]

VARIANT = sys.argv[1] if len(sys.argv) > 1 else 'prata'
SERIF = {'prata': 'prata', 'oranienbaum': 'oranienbaum', 'cormorant': 'cormorant-garamond', 'cormorant-light': 'cormorant-garamond', 'cormorant-medium': 'cormorant-garamond'}[VARIANT]
SERIF_W = {'cormorant-light': 300, 'cormorant-medium': 500}.get(VARIANT, 400)
OUT = Path('logo-svg') / f'type-{VARIANT}'; OUT.mkdir(parents=True, exist_ok=True)

class Face:
    def __init__(self, path):
        self.f = TTFont(path); self.gs = self.f.getGlyphSet(); self.cmap = self.f.getBestCmap()
        self.upm = self.f['head'].unitsPerEm
    def glyph(self, ch):
        return self.gs[self.cmap[ord(ch)]]
    def cap(self):
        b = BoundsPen(self.gs); self.glyph('H' if 0x48 in self.cmap else 'Н').draw(b); return b.bounds[3]
    def text(self, s, size, spacing=0.0):
        """Контуры строки: path d, ширина. spacing — доля em между буквами."""
        k = size / self.upm; x = 0; parts = []
        for i, ch in enumerate(s):
            if ch == ' ':
                x += size * 0.55; continue
            g = self.glyph(ch)
            pen = SVGPathPen(self.gs)
            g.draw(TransformPen(pen, (k, 0, 0, -k, x, 0)))   # y вверх → вниз
            parts.append(pen.getCommands())
            x += g.width * k + (spacing * size if i < len(s) - 1 else 0)
        return ' '.join(parts), x

serif_cy = Face(ff(SERIF, 'cyrillic', SERIF_W))
serif_la = Face(ff(SERIF, 'latin', SERIF_W))
sans = Face(ff('manrope', 'cyrillic', 400))

# --- геометрия в px референса (viewBox 480×545) ---
W, H = 480, 545
CX = 240
els = []  # (d, class)

def place(d, w, cx, baseline):
    return f'<g transform="translate({cx - w / 2:.2f},{baseline:.2f})"><path d="{d}"/></g>'

# знак P/S: две буквы и тонкая диагональ
mk = 205 / 1.0                                            # ширина знака в референсе
size_ps = 170 * serif_la.upm / serif_la.cap()             # кегль: высота P = 170 px референса
dP, wP = serif_la.text('P', size_ps); dS, wS = serif_la.text('S', size_ps)
capP = 170
# P: левый верх; S: правый низ; между ними просвет
gap = -wP * 0.36                                          # S заходит под чашу P
total = wP + gap + wS
x0 = CX - total / 2
top = 30
sy = top + capP * 1.72                                    # базовая линия S
mark = (f'<g class="lg-br" transform="translate({x0:.1f},{top + capP:.1f})"><path d="{dP}"/></g>'
        f'<g class="lg-br" transform="translate({x0 + wP + gap:.1f},{sy:.1f})"><path d="{dS}"/></g>')
# диагональ: снизу-слева вверх-направо, между буквами
lx0, ly0 = x0 + wP * 0.30, sy + 12
lx1, ly1 = x0 + wP + gap + wS * 0.78, top - 16
mark += f'<line class="lg-brs" x1="{lx0:.1f}" y1="{ly0:.1f}" x2="{lx1:.1f}" y2="{ly1:.1f}"/>'
els.append(mark)
mark_bottom = sy + 6

# ПРОХОРОВА
_, w100 = serif_cy.text('ПРОХОРОВА', 100, spacing=0.34); name_size = 100 * 435 / w100   # ширина 435 px референса
dN, wN = serif_cy.text('ПРОХОРОВА', name_size, spacing=0.34)
y_name = mark_bottom + 34 + serif_cy.cap() * name_size / serif_cy.upm
els.append(f'<g class="lg-ink">{place(dN, wN, CX, y_name)}</g>')

# SELECT
_, w100 = serif_la.text('SELECT', 100, spacing=0.48); sel_size = 100 * 212 / w100
dSel, wSel = serif_la.text('SELECT', sel_size, spacing=0.48)
y_sel = y_name + 54
els.append(f'<g class="lg-br">{place(dSel, wSel, CX, y_sel)}</g>')

# черта
y_rule = y_sel + 40
els.append(f'<line class="lg-brs" x1="{CX - 36}" y1="{y_rule}" x2="{CX + 36}" y2="{y_rule}"/>')

# подпись
_, w100 = sans.text('ЛЮДИ    МЕСТА    ВОЗМОЖНОСТИ', 100, spacing=0.30); tag_size = 100 * 425 / w100
dT, wT = sans.text('ЛЮДИ    МЕСТА    ВОЗМОЖНОСТИ', tag_size, spacing=0.30)
y_tag = y_rule + 44
els.append(f'<g class="lg-br">{place(dT, wT, CX, y_tag)}</g>')
H = int(y_tag + 24)

body = ''.join(els)
(OUT / 'logo-inline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>')

GRAD = {'bronze': ('#C9A97E', '#8E6F4B', '#5E4630'), 'bronzeDark': ('#E2C89E', '#B8976A', '#8A6C48')}
def full(ink, gid, bg=None):
    a, b, c = GRAD[gid]
    defs = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset=".45" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient></defs>'
            f'<style>.lg-ink{{fill:{ink}}}.lg-br{{fill:url(#g)}}.lg-brs{{stroke:{b};stroke-width:1.5;stroke-linecap:round}}</style>')
    rect = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{rect}{body}</svg>'
(OUT / 'logo-light.svg').write_text(full('#1F1B17', 'bronze'))
(OUT / 'logo-dark.svg').write_text(full('#ECE5DB', 'bronzeDark'))
(OUT / 'logo-light-bg.svg').write_text(full('#1F1B17', 'bronze', '#E4DDD4'))
(OUT / 'logo-dark-bg.svg').write_text(full('#ECE5DB', 'bronzeDark', '#1A1917'))
# знак отдельно
mw, mh = total + 40, mark_bottom - top + 40
mark_only = mark.replace(f'translate({x0:.1f},', f'translate({20:.1f},').replace(f'translate({x0 + wP + gap:.1f},', f'translate({20 + wP + gap:.1f},')
# смещаем по y на -top+20 и по x на -x0+20 через обёртку
(OUT / 'mark-inline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw:.0f} {mh:.0f}"><g transform="translate({20 - x0:.1f},{20 - top:.1f})">{mark}</g></svg>')
for name, gid, ink in (('mark-light', 'bronze', '#1F1B17'), ('mark-dark', 'bronzeDark', '#ECE5DB')):
    a, b, c = GRAD[gid]
    (OUT / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw:.0f} {mh:.0f}" width="{mw:.0f}" height="{mh:.0f}">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset=".45" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient></defs>'
        f'<style>.lg-br{{fill:url(#g)}}.lg-brs{{stroke:{b};stroke-width:1.5;stroke-linecap:round}}</style><g transform="translate({20 - x0:.1f},{20 - top:.1f})">{mark}</g></svg>')
print('готово:', OUT, 'размер', W, H)
