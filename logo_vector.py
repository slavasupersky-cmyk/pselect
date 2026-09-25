#!/usr/bin/env python3
"""
Векторизация лого «Прохорова Select» из растрового макета (potrace).

Режет макет на элементы, увеличивает, переводит в маску по яркости, обводит и собирает
SVG: цвета через CSS-классы (lg-ink, lg-br) — сайт красит их под тему; плюс автономные
файлы со вшитыми цветами (светлый/тёмный, с фоном и без) и отдельный знак.

Нужен potrace:  brew install potrace  |  apt install potrace
Запуск:  python3 logo_vector.py <вариант>   (варианты описаны в VARIANTS ниже)
"""
import re, subprocess, sys
from pathlib import Path
from PIL import Image

# Вариант: файл, режим (dark — светлые буквы на тёмном), увеличение, порог яркости,
# элементы (x0,y0,x1,y1, роль: ink — цвет текста, bronze — бронзовый градиент; порог можно задать свой),
# рамка композиции.
VARIANTS = {
    'ps-mono': dict(src='logo.jpg', dark=False, scale=4, thresh=195, frame=(260, 70, 995, 755), parts={
        'mark': ((470, 80, 770, 490), 'bronze'), 'name': ((270, 500, 985, 590), 'ink'),
        'select': ((445, 595, 800, 655), 'bronze'), 'line': ((560, 672, 700, 688), 'bronze'),
        'sub': ((420, 712, 830, 745), 'bronze')}),
    'ps-slash': dict(src='logo2.png', dark=True, scale=6, thresh=55, frame=(80, 40, 560, 585), parts={
        'mark': ((200, 50, 405, 350), 'bronze'), 'name': ((95, 370, 530, 418), 'ink'),
        'select': ((205, 433, 420, 466), 'bronze'), 'line': ((275, 500, 350, 512), 'bronze', 50),
        'sub': ((85, 548, 545, 572), 'bronze')}),
}
V = VARIANTS[sys.argv[1] if len(sys.argv) > 1 else 'ps-slash']
OUT = Path('logo-svg') / (sys.argv[1] if len(sys.argv) > 1 else 'ps-slash'); OUT.mkdir(parents=True, exist_ok=True)
im = Image.open(V['src']).convert('L')
S = V['scale']

def trace(box, thresh):
    x0, y0, x1, y1 = box
    crop = im.crop(box).resize(((x1 - x0) * S, (y1 - y0) * S), Image.LANCZOS)
    # маска: чёрное = фигура
    if V['dark']: mask = crop.point(lambda v: 0 if v > thresh else 255)
    else:        mask = crop.point(lambda v: 0 if v < thresh else 255)
    pbm, svg = OUT / '_tmp.pbm', OUT / '_tmp.svg'
    mask.convert('1').save(pbm)
    subprocess.run(['potrace', str(pbm), '-s', '-o', str(svg), '-a', '1.3', '-O', '0.25', '-t', str(4 * S // 2), '--flat'], check=True)
    txt = svg.read_text()
    d = ' '.join(re.findall(r'd="([^"]+)"', txt))
    tr = re.search(r'<g transform="([^"]+)"', txt).group(1)
    return x0, y0, d, tr

paths = {}
for k, spec in V['parts'].items():
    box, role = spec[0], spec[1]
    paths[k] = (role,) + trace(box, spec[2] if len(spec) > 2 else V['thresh'])
for f in ('_tmp.pbm', '_tmp.svg'): (OUT / f).unlink(missing_ok=True)

X0, Y0, X1, Y1 = V['frame']; W, H = X1 - X0, Y1 - Y0
def group(k, fill):
    role, x0, y0, d, tr = paths[k]
    return f'<g transform="translate({x0 - X0},{y0 - Y0}) scale({1 / S})"><g transform="{tr}"><path {fill} d="{d}"/></g></g>'

GRAD = {'bronze': ('#C9A97E', '#8E6F4B', '#5E4630'), 'bronzeDark': ('#E2C89E', '#B8976A', '#8A6C48')}
def defs(gid):
    a, b, c = GRAD[gid]
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset=".45" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient></defs>')

def compose(ink, gid, bg=None):
    body = ''.join(group(k, f'fill="{ink}"' if paths[k][0] == 'ink' else f'fill="url(#{gid})"') for k in paths)
    rect = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs(gid)}{rect}{body}</svg>'

(OUT / 'logo-light.svg').write_text(compose('#1F1B17', 'bronze'))
(OUT / 'logo-dark.svg').write_text(compose('#ECE5DB', 'bronzeDark'))
(OUT / 'logo-light-bg.svg').write_text(compose('#1F1B17', 'bronze', '#E4DDD4'))
(OUT / 'logo-dark-bg.svg').write_text(compose('#ECE5DB', 'bronzeDark', '#1A1917'))
# для сайта: цвета классами, градиент задаёт страница
body = ''.join(group(k, 'class="lg-ink"' if paths[k][0] == 'ink' else 'class="lg-br"') for k in paths)
(OUT / 'logo-inline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{body}</svg>')
role, mx0, my0, md, mtr = paths['mark']; mb = V['parts']['mark'][0]; mw, mh = mb[2] - mb[0], mb[3] - mb[1]
(OUT / 'mark-inline.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw} {mh}"><g transform="scale({1 / S})"><g transform="{mtr}"><path class="lg-br" d="{md}"/></g></g></svg>')
for name, gid in (('mark-light', 'bronze'), ('mark-dark', 'bronzeDark')):
    (OUT / f'{name}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mw} {mh}" width="{mw}" height="{mh}">{defs(gid)}'
                                     f'<g transform="scale({1 / S})"><g transform="{mtr}"><path fill="url(#{gid})" d="{md}"/></g></g></svg>')
print('готово:', OUT, sorted(p.name for p in OUT.iterdir()))
