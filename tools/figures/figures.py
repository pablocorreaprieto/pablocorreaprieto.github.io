#!/usr/bin/env python3
"""Generates the SVG sources of the article figures (not the covers).

    python3 tools/figures/figures.py            # all figures, all languages present in TEXT
    node tools/figures/render.mjs tools/figures/svg/*.svg

Each figure is 1800×945, in the site's style (kicker, serif title, footer with
name and domain, credit line bottom right). Text lines are broken by hand in
TEXT; render.mjs warns when a line is wider than its data-maxw.

Charts use only published, cited data (the source line is part of the figure).
Colours: site palette; the two data hues (#2F6DB0, #B8492A) pass the dataviz
palette validator on the #FAFAF8 surface.
"""
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'svg')
W, H = 1800, 945
L, R = 115, 1685  # content margins

C = dict(ground='#FAFAF8', soft='#E8EDF2', ink='#1C2128', muted='#5B626C', faint='#6C737C',
         rule='#E2E3DF', accent='#264A6E', mark='#B8492A', blue='#2F6DB0', white='#FFFFFF')
SERIF = "'Source Serif 4', Georgia, serif"
SANS = "'IBM Plex Sans', Helvetica, Arial, sans-serif"
FONTS = '../../title-card/fonts/'

FOOT = {
    'fr': ' · enseignant et recherche en éducation',
    'en': ' · teacher and education researcher',
    'es': ' · docente e investigador en educación',
}


def t(x, y, s, size=28, fill=None, weight=400, family=SANS, anchor='start', ls=None, maxw=None, extra=''):
    fill = fill or C['ink']
    a = f' letter-spacing="{ls}"' if ls else ''
    m = f' data-maxw="{maxw}"' if maxw else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{a}{m}{extra}>{s}</text>')


def lines(x, y, rows, size=28, lh=1.4, **kw):
    out = []
    for i, r in enumerate(rows):
        out.append(t(x, round(y + i * size * lh), escape(r), size=size, **kw))
    return '\n'.join(out)


def title_text(s):
    """Serif title; a trailing '.' is drawn in the accent colour (as on the covers)."""
    s = escape(s)
    if s.endswith('.'):
        return s[:-1] + f'<tspan fill="{C["mark"]}">.</tspan>'
    return s


def frame(lang, kicker, title, body, source=None, bg='ground', title_size=76):
    src = ''
    if source:
        src = lines(L, 752, source, size=19, fill=C['muted'], lh=1.45, maxw=R - L)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" lang="{lang}">
<defs>
<style>
@font-face{{font-family:'Source Serif 4'; src:url({FONTS}source-serif-4-latin-opsz-normal.woff2) format('woff2'); font-weight:200 900}}
@font-face{{font-family:'IBM Plex Sans'; src:url({FONTS}ibm-plex-sans-latin-400-normal.woff2) format('woff2'); font-weight:400}}
@font-face{{font-family:'IBM Plex Sans'; src:url({FONTS}ibm-plex-sans-latin-500-normal.woff2) format('woff2'); font-weight:500}}
@font-face{{font-family:'IBM Plex Sans'; src:url({FONTS}ibm-plex-sans-latin-600-normal.woff2) format('woff2'); font-weight:600}}
.serif{{font-variation-settings:'opsz' 60}}
</style>
<marker id="arrow" viewBox="0 0 12 12" refX="10" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
<path d="M1,1 L10,6 L1,11" fill="none" stroke="{C['accent']}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</marker>
</defs>
<rect width="{W}" height="{H}" fill="{C[bg]}"/>
{t(L, 111, escape(kicker.upper()), size=25, weight=600, fill=C['accent'], ls='4', maxw=R - L)}
<text class="serif" x="{L - 3}" y="228" font-family="{SERIF}" font-size="{title_size}" font-weight="450" fill="{C['ink']}" letter-spacing="-1.5" data-maxw="{R - L}">{title_text(title)}</text>
{body}
{src}
<line x1="{L}" y1="795" x2="{R}" y2="795" stroke="{C['rule']}" stroke-width="2"/>
<text x="{L}" y="855" font-family="{SANS}" font-size="28"><tspan font-weight="600" fill="{C['ink']}">Pablo Correa Prieto</tspan><tspan fill="{C['muted']}">{escape(FOOT[lang])}</tspan></text>
{t(R, 854, 'PABLOCORREAPRIETO.CH', size=22, weight=600, fill=C['accent'], anchor='end', ls='3')}
{t(R, 919, 'Pablo Correa Prieto · 2026 · CC BY 4.0', size=17, fill=C['faint'], anchor='end')}
</svg>
'''


def rrect(x, y, w, h, r=6, fill='none', stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{s}/>'


def column_bar(x, base, w, h, fill, r=10):
    """Vertical bar growing from the baseline; rounded data end, square at the baseline."""
    top = base - h
    r = min(r, h / 2, w / 2)
    return (f'<path d="M{x},{base} L{x},{top + r} Q{x},{top} {x + r},{top} L{x + w - r},{top} '
            f'Q{x + w},{top} {x + w},{top + r} L{x + w},{base} Z" fill="{fill}"/>')


def hbar(x0, y, length, h, fill, r=10):
    """Horizontal bar from x0; positive length grows right, negative grows left. Rounded data end."""
    if length == 0:
        return ''
    r = min(r, abs(length) / 2, h / 2)
    if length > 0:
        x1 = x0 + length
        return (f'<path d="M{x0},{y} L{x1 - r},{y} Q{x1},{y} {x1},{y + r} L{x1},{y + h - r} '
                f'Q{x1},{y + h} {x1 - r},{y + h} L{x0},{y + h} Z" fill="{fill}"/>')
    x1 = x0 + length
    return (f'<path d="M{x0},{y} L{x1 + r},{y} Q{x1},{y} {x1},{y + r} L{x1},{y + h - r} '
            f'Q{x1},{y + h} {x1 + r},{y + h} L{x0},{y + h} Z" fill="{fill}"/>')


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C["accent"]}" stroke-width="2.2" '
            f'stroke-linecap="round" marker-end="url(#arrow)"/>')


def elbow(x1, y1, x2, y2):
    """Horizontal-vertical-horizontal connector with an arrow at the end."""
    xm = (x1 + x2) / 2
    return (f'<path d="M{x1},{y1} L{xm},{y1} L{xm},{y2} L{x2},{y2}" fill="none" stroke="{C["accent"]}" '
            f'stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" marker-end="url(#arrow)"/>')


def box(x, y, w, h, label, rows, emph=False, size=34, bg='white'):
    """Box with a small uppercase label and serif text rows."""
    out = [rrect(x, y, w, h, fill=C[bg], stroke=C['mark'] if emph else C['rule'], sw=2)]
    if label:
        out.append(t(x + 30, y + 44, escape(label.upper()), size=19, weight=600, fill=C['accent'], ls='3', maxw=w - 60))
    y0 = y + (88 if label else 60)
    for i, r in enumerate(rows):
        out.append(f'<text class="serif" x="{x + 30}" y="{y0 + i * round(size * 1.25)}" font-family="{SERIF}" '
                   f'font-size="{size}" font-weight="450" fill="{C["ink"]}" data-maxw="{w - 60}">{escape(r)}</text>')
    return '\n'.join(out)


# ---------------------------------------------------------------- figures

def fig_meme_copie(lang, T):
    """Brimi (2011): letter grades given by 73 teachers to the same paper."""
    data = [('A', 10), ('B', 18), ('C', 30), ('D', 9), ('F', 6)]
    base, scale, bw, gap, x0 = 650, 10, 64, 150, L + 10
    body = [lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=1000)]
    body.append(f'<line x1="{L}" y1="{base}" x2="{L + 5 * gap + 10}" y2="{base}" stroke="{C["rule"]}" stroke-width="2"/>')
    for i, (k, v) in enumerate(data):
        x = x0 + i * gap
        body.append(column_bar(x, base, bw, v * scale, C['blue']))
        body.append(t(x + bw / 2, base - v * scale - 16, str(v), size=30, weight=600, anchor='middle'))
        body.append(t(x + bw / 2, base + 42, k, size=30, weight=500, fill=C['muted'], anchor='middle'))
    # side panel: two stat blocks
    px = 1010
    body.append(f'<line x1="{px}" y1="330" x2="{px}" y2="700" stroke="{C["rule"]}" stroke-width="2"/>')
    body.append(t(px + 60, 420, T['stat1'], size=76, weight=600))
    body.append(lines(px + 60, 470, T['stat1_label'], size=26, fill=C['muted'], maxw=600))
    body.append(t(px + 60, 610, T['stat2'], size=76, weight=600))
    body.append(lines(px + 60, 660, T['stat2_label'], size=26, fill=C['muted'], maxw=600))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(body), T['source'])


def fig_second_regard(lang, T):
    """Second-reader workflow (after the parallel-marking design described by Ofqual)."""
    b = []
    b.append(box(L, 425, 300, 150, T['b1_label'], T['b1']))
    b.append(box(505, 290, 400, 150, T['b2_label'], T['b2']))
    b.append(box(505, 560, 400, 150, T['b3_label'], T['b3']))
    b.append(box(995, 425, 300, 150, T['b4_label'], T['b4']))
    b.append(box(1385, 290, 300, 150, T['b5_label'], T['b5']))
    b.append(box(1385, 560, 300, 150, T['b6_label'], T['b6'], emph=True))
    b.append(elbow(L + 300, 500, 497, 365))
    b.append(elbow(L + 300, 500, 497, 635))
    b.append(elbow(905, 365, 987, 500))
    b.append(elbow(905, 635, 987, 500))
    b.append(elbow(1295, 500, 1377, 365))
    b.append(elbow(1295, 500, 1377, 635))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_three_questions(lang, T):
    """Three separate questions for judging an assessment item."""
    b = []
    cols = [(L, T['c1']), (L + 543, T['c2']), (L + 1086, T['c3'])]
    for i, (x, (head, rows)) in enumerate(cols):
        b.append(f'<line x1="{x}" y1="300" x2="{x + 484}" y2="300" stroke="{C["rule"]}" stroke-width="2"/>')
        b.append(f'<text class="serif" x="{x}" y="398" font-family="{SERIF}" font-size="72" font-weight="400" fill="{C["mark"]}">{i + 1}</text>')
        b.append(f'<text class="serif" x="{x}" y="478" font-family="{SERIF}" font-size="44" font-weight="500" fill="{C["ink"]}" data-maxw="484">{escape(head)}</text>')
        b.append(lines(x, 532, rows, size=29, fill=C['muted'], maxw=484))
    b.append(t(L, 710, escape(T['note']), size=30, weight=500, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T.get('source'), bg='soft')


def fig_levels(lang, T):
    """Two published grids of cognitive demand, low to high (translated labels)."""
    b = []
    colw, rowh, gaph = 700, 72, 14
    for ci, (x, head, sub, items) in enumerate([(L + 60, T['h1'], T['s1'], T['l1']), (L + 830, T['h2'], T['s2'], T['l2'])]):
        b.append(t(x, 300, escape(head), size=30, weight=600, maxw=colw))
        b.append(t(x, 336, escape(sub), size=22, fill=C['muted'], maxw=colw))
        for i, item in enumerate(items):  # i = 0 is the lowest level, drawn at the bottom
            y = 624 - i * (rowh + gaph)
            indent = i * 34
            b.append(rrect(x + indent, y, colw - 3 * 34, rowh, fill=C['white'], stroke=C['rule']))
            b.append(f'<rect x="{x + indent}" y="{y}" width="8" height="{rowh}" rx="3" fill="{C["blue"]}"/>')
            b.append(f'<text class="serif" x="{x + indent + 30}" y="{y + 48}" font-family="{SERIF}" font-size="30" fill="{C["mark"]}">{i + 1}</text>')
            b.append(t(x + indent + 70, y + 47, escape(item), size=28, weight=500, maxw=colw - 3 * 34 - 90))
    # vertical axis: increasing demand
    b.append(f'<line x1="{L + 18}" y1="694" x2="{L + 18}" y2="376" stroke="{C["accent"]}" stroke-width="2.2" stroke-linecap="round" marker-end="url(#arrow)"/>')
    b.append(f'<text x="{L + 2}" y="536" font-family="{SANS}" font-size="20" font-weight="600" fill="{C["accent"]}" letter-spacing="3" transform="rotate(-90 {L + 2} 536)" text-anchor="middle">{escape(T["axis"].upper())}</text>')
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_ia_examen(lang, T):
    """Bastani et al. (2025): change in grades vs the no-AI control arm, during practice and on the exam."""
    b = []
    zero, scale, bh, step, head = 820, 5.0, 38, 52, 46
    b.append(lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=R - L))
    # legend
    ly = 344
    b.append(f'<rect x="{L}" y="{ly - 18}" width="22" height="22" rx="4" fill="{C["blue"]}"/>')
    b.append(t(L + 34, ly, escape(T['leg1']), size=24, fill=C['ink']))
    l2 = T.get('leg2x', 520)
    b.append(f'<rect x="{L + l2}" y="{ly - 18}" width="22" height="22" rx="4" fill="{C["mark"]}"/>')
    b.append(t(L + l2 + 34, ly, escape(T['leg2']), size=24, fill=C['ink']))
    rows = [
        (T['arm1'], None, None),
        (T['r_practice'], 48, 'blue'),
        (T['r_exam'], -17, 'mark'),
        (T['arm2'], None, None),
        (T['r_practice'], 127, 'blue'),
        (T['r_exam'], 0, 'mark'),
    ]
    y, top = 378, 378
    for label, v, col in rows:
        if v is None:
            b.append(t(L, y + 30, escape(label), size=26, weight=600, maxw=640))
            y += head
            continue
        b.append(t(L + 24, y + 28, escape(label), size=24, fill=C['muted'], maxw=560))
        if v == 0:
            b.append(t(zero + 16, y + 28, escape(T['ns']), size=24, weight=500, fill=C['ink']))
        else:
            b.append(hbar(zero, y, v * scale, bh, C[col]))
            lab = ('+' if v > 0 else '−') + (f'{abs(v)}%' if lang == 'en' else f'{abs(v)} %')
            if v > 0:
                b.append(t(zero + v * scale + 14, y + 29, lab, size=26, weight=600))
            else:
                b.append(t(zero + v * scale - 12, y + 29, lab, size=26, weight=600, anchor='end'))
        y += step
    b.append(f'<line x1="{zero}" y1="{top}" x2="{zero}" y2="{y - 8}" stroke="{C["muted"]}" stroke-width="2"/>')
    b.append(t(zero, y + 18, escape(T['zero']), size=20, fill=C['muted'], anchor='middle'))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_garder_confier(lang, T):
    """Proposal: keep demanding what is the learning; hand to the tool what is only a means."""
    b = []
    for ci, (x, head, sub, items, col) in enumerate([
            (L, T['h1'], T['s1'], T['l1'], C['mark']),
            (L + 800, T['h2'], T['s2'], T['l2'], C['blue'])]):
        b.append(f'<rect x="{x}" y="290" width="770" height="6" rx="3" fill="{col}"/>')
        b.append(f'<text class="serif" x="{x}" y="358" font-family="{SERIF}" font-size="46" font-weight="500" fill="{C["ink"]}" data-maxw="770">{escape(head)}</text>')
        b.append(t(x, 400, escape(sub), size=25, fill=C['muted'], maxw=770))
        for i, it in enumerate(items):
            yy = 470 + i * 58
            b.append(f'<circle cx="{x + 9}" cy="{yy - 9}" r="6" fill="{col}"/>')
            b.append(t(x + 32, yy, escape(it), size=28, maxw=735))
    b.append(t(L, 700, escape(T['note']), size=26, weight=500, fill=C['ink'], maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'], bg='ground')


def fig_temps_gagne(lang, T):
    """Roy et al. (2024), EEF/NFER: weekly lesson-preparation time, with and without ChatGPT."""
    b = [lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    x0, scale, bh = L + 470, 9.0, 60
    rows = [(T['r1'], 81.5, C['muted']), (T['r2'], 56.2, C['blue'])]
    for i, (label, v, col) in enumerate(rows):
        y = 380 + i * 120
        b.append(lines(L, y + 26, label, size=26, fill=C['ink'], maxw=440, lh=1.3))
        b.append(hbar(x0, y, v * scale, bh, col))
        b.append(t(x0 + v * scale + 16, y + 41, T['fmt'](v), size=30, weight=600))
    b.append(f'<line x1="{x0}" y1="366" x2="{x0}" y2="{380 + 2 * 120 - 46}" stroke="{C["rule"]}" stroke-width="2"/>')
    # difference annotation
    xa, xb, ya = x0 + 56.2 * scale, x0 + 81.5 * scale, 598
    b.append(f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{ya}" stroke="{C["mark"]}" stroke-width="2.2"/>')
    b.append(f'<line x1="{xa}" y1="{ya - 10}" x2="{xa}" y2="{ya + 10}" stroke="{C["mark"]}" stroke-width="2.2"/>')
    b.append(f'<line x1="{xb}" y1="{ya - 10}" x2="{xb}" y2="{ya + 10}" stroke="{C["mark"]}" stroke-width="2.2"/>')
    b.append(t((xa + xb) / 2, ya + 42, escape(T['diff']), size=26, weight=600, fill=C['ink'], anchor='middle'))
    b.append(lines(L, 700, T['quality'], size=24, fill=C['muted'], maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_verifier(lang, T):
    """Proposal: generate, check, adapt; checking is the real work."""
    b = []
    xs = [L, L + 560, L + 1120]
    wds = [450, 450, 450]
    for i, (x, w) in enumerate(zip(xs, wds)):
        emph = i == 1
        b.append(rrect(x, 290, w, 420, fill=C['white'], stroke=C['mark'] if emph else C['rule'], sw=2.5 if emph else 2))
        b.append(f'<text class="serif" x="{x + 34}" y="370" font-family="{SERIF}" font-size="56" fill="{C["mark"]}">{i + 1}</text>')
        head, rows = T[f'c{i + 1}']
        b.append(f'<text class="serif" x="{x + 34}" y="440" font-family="{SERIF}" font-size="44" font-weight="500" fill="{C["ink"]}" data-maxw="{w - 68}">{escape(head)}</text>')
        if i == 1:
            for j, r in enumerate(rows):
                yy = 500 + j * 78
                b.append(f'<path d="M{x + 36},{yy - 10} l8,9 l16,-19" fill="none" stroke="{C["mark"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
                b.append(lines(x + 74, yy, r, size=26, fill=C['ink'], maxw=w - 108, lh=1.25))
        else:
            b.append(lines(x + 34, 500, rows, size=27, fill=C['muted'], maxw=w - 68))
    b.append(arrow(L + 460, 500, L + 550, 500))
    b.append(arrow(L + 1020, 500, L + 1110, 500))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_detect_exactitude(lang, T):
    """Weber-Wulff et al. (2023): mean accuracy of 14 detectors by document class (binary approach)."""
    b = [lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    x0, scale, bh, step = 840, 7.8, 40, 58
    y = 356
    for label, v, col in T['rows']:
        b.append(t(L, y + 29, escape(label), size=26, maxw=x0 - L - 40))
        b.append(hbar(x0, y, v * scale, bh, C[col]))
        b.append(t(x0 + v * scale + 16, y + 30, escape(T['pct'].format(v)), size=26, weight=600))
        y += step
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_detect_decision(lang, T):
    """What a detector outputs versus what a decision requires."""
    b = [box(L, 322, 740, 282, T['c1_label'], T['c1']),
         box(945, 322, 740, 282, T['c2_label'], T['c2'], emph=True)]
    b.append(lines(L, 664, T['note'], size=27, weight=500, lh=1.35, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'], bg='soft')


def fig_acc_correlations(lang, T):
    """Davis (1989) and Parry et al. (2021): what the correlations are actually between."""
    b = [lines(L, 288, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    scale, bh = 1000, 38
    y = 340
    for label, v, disp, note, col in T['rows']:
        b.append(t(L, y, escape(label), size=27, weight=500, maxw=R - L))
        b.append(hbar(L, y + 16, v * scale, bh, C[col]))
        b.append(t(L + v * scale + 18, y + 45, escape(disp), size=30, weight=600))
        b.append(lines(L, y + 86, note, size=22, fill=C['muted'], lh=1.3, maxw=1180))
        y += 126
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_acc_chaine(lang, T):
    """Where the validation of acceptance models stops."""
    w, gap, y, h = 350, 55, 390, 120
    xs = [L + i * (w + gap) for i in range(4)]
    b = [lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    for i, (x, rows) in enumerate(zip(xs, T['boxes'])):
        b.append(box(x, y, w, h, None, rows, emph=(i == 3)))
    for i in range(3):
        b.append(arrow(xs[i] + w + 6, y + h / 2, xs[i + 1] - 6, y + h / 2))
    by = y + h + 38
    b.append(f'<path d="M{xs[0]},{by} L{xs[0]},{by + 14} L{xs[2] + w},{by + 14} L{xs[2] + w},{by}" '
             f'fill="none" stroke="{C["rule"]}" stroke-width="2"/>')
    b.append(f'<path d="M{xs[3]},{by} L{xs[3]},{by + 14} L{xs[3] + w},{by + 14} L{xs[3] + w},{by}" '
             f'fill="none" stroke="{C["mark"]}" stroke-width="2"/>')
    b.append(lines((xs[0] + xs[2] + w) / 2, by + 58, T['brace1'], size=26, fill=C['muted'],
                   anchor='middle', maxw=1040))
    b.append(lines(xs[3] + w / 2, by + 58, T['brace2'], size=26, weight=600, fill=C['mark'],
                   anchor='middle', maxw=w + 80))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_fb_information(lang, T):
    """Wisniewski et al. (2020): effect size by the information content of the feedback."""
    base, scale, bw = 665, 320, 170
    xs = [375, 815, 1255]
    b = [lines(L, 288, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    ry = round(base - 0.48 * scale)
    b.append(f'<line x1="{L}" y1="{ry}" x2="{R}" y2="{ry}" stroke="{C["muted"]}" stroke-width="2" '
             f'stroke-dasharray="7 7"/>')
    b.append(t(R, ry - 14, escape(T['ref']), size=22, fill=C['muted'], anchor='end'))
    b.append(f'<line x1="{L}" y1="{base}" x2="{R}" y2="{base}" stroke="{C["rule"]}" stroke-width="2"/>')
    for x, (label, v, disp) in zip(xs, T['bars']):
        b.append(column_bar(x, base, bw, round(v * scale), C['blue']))
        b.append(t(x + bw / 2, base - v * scale - 18, escape(disp), size=34, weight=600, anchor='middle'))
        b.append(lines(x + bw / 2, base + 42, label, size=23, fill=C['muted'], anchor='middle', maxw=430))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_fb_ia_expert(lang, T):
    """Jansen et al. (2024): feedback judged useful for revision, raters blind to the source."""
    b = [lines(L, 290, T['sub'], size=28, fill=C['muted'], maxw=R - L)]
    x0, scale, bh, step = 900, 7.2, 46, 96
    y = 390
    for label, v, col in T['rows']:
        b.append(lines(L, y + 20, label, size=26, lh=1.3, maxw=x0 - L - 40))
        b.append(hbar(x0, y, v * scale, bh, C[col]))
        b.append(t(x0 + v * scale + 18, y + 34, escape(T['pct'].format(v)), size=30, weight=600))
        y += step
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


FIGS = {
    'correction-meme-copie': fig_meme_copie,
    'correction-second-regard': fig_second_regard,
    'items-trois-questions': fig_three_questions,
    'items-exigence-cognitive': fig_levels,
    'effort-ia-examen': fig_ia_examen,
    'effort-garder-confier': fig_garder_confier,
    'preparer-temps-gagne': fig_temps_gagne,
    'preparer-verifier': fig_verifier,
    'detecteurs-exactitude': fig_detect_exactitude,
    'detecteurs-decision': fig_detect_decision,
    'acceptation-correlations': fig_acc_correlations,
    'acceptation-chaine': fig_acc_chaine,
    'feedback-information': fig_fb_information,
    'feedback-ia-expert': fig_fb_ia_expert,
}


def fr_min(v):
    return f'{v:.1f}'.replace('.', ',') + ' min'


def en_min(v):
    return f'{v:.1f} min'


TEXT = {
    'fr': {
        'detecteurs-exactitude': dict(
            kicker='Détection · données publiées',
            title='Ce que les détecteurs réussissent, et où ils échouent.',
            sub=['Exactitude moyenne de quatorze outils de détection selon le type de document, approche binaire'],
            pct='{} %',
            rows=[('Texte écrit par un humain', 94, 'blue'),
                  ('Texte traduit automatiquement', 69, 'blue'),
                  ('Texte généré par IA (série 1)', 63, 'blue'),
                  ('Texte généré par IA (série 2)', 70, 'blue'),
                  ('Texte d\u2019IA retouché à la main', 30, 'mark'),
                  ('Texte d\u2019IA passé par un paraphraseur', 15, 'mark')],
            source=['Données : Weber-Wulff, D. et al. (2023). Testing of detection tools for AI-generated text.',
                    'International Journal for Educational Integrity, 19(1), 26. Graphique : Pablo Correa Prieto.'],
        ),
        'detecteurs-decision': dict(
            kicker='Détection · analyse',
            title='Une probabilité n\u2019est pas une preuve.',
            c1_label='Ce qu\u2019un détecteur produit',
            c1=['Une probabilité', 'Portant sur un texte', 'Sans distinguer ses', 'propres erreurs'],
            c2_label='Ce qu\u2019une décision exige',
            c2=['Une certitude suffisante', 'Portant sur une personne', 'et sur un acte', 'À laquelle l\u2019élève', 'puisse répondre'],
            note=['Aucune information dans la sortie de l\u2019outil ne distingue',
                  'le signalement juste du signalement erroné.'],
            source=['Analyse de l\u2019auteur, à partir de Weber-Wulff et al. (2023), Van Vlasselaer et al. (2026) et des recommandations',
                    'de la CIIP (2025). Schéma : Pablo Correa Prieto.'],
        ),
        'acceptation-correlations': dict(
            kicker='Mesure · données publiées',
            title='Des corrélations entre déclarations.',
            sub=['Ce que mesurent réellement les corrélations citées à l\u2019appui des modèles d\u2019acceptation'],
            rows=[('Utilité perçue ↔ usage futur auto-prédit', 0.85, '0,85',
                   ['Davis (1989). Deux réponses de la même personne, dans le même questionnaire.'], 'blue'),
                  ('Utilité perçue ↔ usage déclaré', 0.63, '0,63',
                   ['Davis (1989). Également déclaratif.'], 'blue'),
                  ('Usage déclaré ↔ usage enregistré', 0.38, '0,38',
                   ['Parry et al. (2021). Méta-analyse de 44 études, N = 52 007. Seules 6 % des estimations',
                    'déclarées moyennes tombent à moins de 5 % de la moyenne enregistrée.'], 'mark')],
            source=['Données : Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340 ; Parry, D. A. et al. (2021).',
                    'Nature Human Behaviour, 5(11), 1535–1547. Graphique : Pablo Correa Prieto.'],
        ),
        'acceptation-chaine': dict(
            kicker='Mesure · analyse',
            title='Où s\u2019arrête la validation.',
            sub=['De l\u2019attitude au comportement : ce que les modèles d\u2019acceptation couvrent réellement'],
            boxes=[['Attitude'], ['Intention'], ['Usage déclaré'], ['Usage enregistré']],
            brace1=['ce que valident les modèles d\u2019acceptation'],
            brace2=['ce qu\u2019on veut', 'savoir'],
            source=['Analyse de l\u2019auteur, à partir de Davis (1989), Straub et al. (1995) et Parry et al. (2021).',
                    'Schéma : Pablo Correa Prieto.'],
        ),
        'feedback-information': dict(
            kicker='Feedback · données publiées',
            title='L\u2019effet suit l\u2019information.',
            sub=['Taille d\u2019effet d\u2019un retour selon ce qu\u2019il contient (435 études, k = 994)'],
            ref='effet global 0,48',
            bars=[(['Renforcer ou sanctionner'], 0.24, '0,24'),
                  (['Retour correctif'], 0.46, '0,46'),
                  (['Retour à haute densité d\u2019information'], 0.99, '0,99')],
            source=['Données : Wisniewski, B., Zierer, K. et Hattie, J. (2020). The power of feedback revisited.',
                    'Frontiers in Psychology, 10, 3087. Graphique : Pablo Correa Prieto.'],
        ),
        'feedback-ia-expert': dict(
            kicker='Feedback · données publiées',
            title='Utile, mais pas au point d\u2019être transmis.',
            sub=['Retours jugés utiles pour la révision par 89 futurs enseignants, la source leur étant inconnue'],
            pct='{} %',
            rows=[(['Retour d\u2019un expert,', 'jugé utile pour la révision'], 88, 'blue'),
                  (['Retour d\u2019un modèle de langage,', 'jugé utile pour la révision'], 59, 'blue'),
                  (['Retour du modèle que l\u2019évaluateur', 'choisit de transmettre à l\u2019élève'], 23, 'mark')],
            source=['Données : Jansen, T. et al. (2024). Comparing generative AI and expert feedback to students\u2019 writing.',
                    'Psychologie in Erziehung und Unterricht, 71(2), 80–92. Graphique : Pablo Correa Prieto.'],
        ),
        'correction-meme-copie': dict(
            kicker='Évaluation · données publiées',
            title='Une même copie, 73 enseignants.',
            sub=['Notes en lettres attribuées à la même rédaction d’élève'],
            stat1='50 à 96',
            stat1_label=['notes sur 100 données à cette', 'même copie par 73 enseignants'],
            stat2='A à F',
            stat2_label=['toutes les lettres de l’échelle,', 'pour un seul et même texte'],
            source=['Données : Brimi, H. M. (2011). Reliability of grading high school work in English. Practical Assessment, Research & Evaluation, 16(17).',
                    'Graphique : Pablo Correa Prieto.'],
        ),
        'correction-second-regard': dict(
            kicker='Évaluation · proposition',
            title='Un second regard, pas un correcteur.',
            b1_label='Copie', b1=['Anonymisée,', 'sans nom'],
            b2_label='Enseignant', b2=['Corrige', 'comme d’habitude'],
            b3_label='IA, en parallèle', b3=['Propose une note', 'ou une remarque'],
            b4_label='Comparer', b4=['Les deux', 'concordent ?'],
            b5_label='Oui', b5=['La note est', 'validée'],
            b6_label='Non', b6=['L’enseignant', 'relit et tranche'],
            source=['D’après le dispositif de notation en parallèle décrit par l’Ofqual (Williamson, 2026). La décision finale reste à l’enseignant.',
                    'Schéma : Pablo Correa Prieto.'],
        ),
        'items-trois-questions': dict(
            kicker='Évaluer un item · trois questions',
            title='Juste ne veut pas dire aligné.',
            c1=('Alignement', ['L’item vise-t-il l’objectif', 'du PER annoncé ?']),
            c2=('Exigence cognitive', ['Quel niveau de réflexion', 'demande-t-il vraiment ?']),
            c3=('Qualité', ['Est-il juste, clair, sans indice,', 'avec une seule bonne réponse ?']),
            note='Un item peut réussir l’une de ces questions et échouer aux deux autres.',
            source=['Cadre de l’étude en préparation de Pablo Correa Prieto (projet OSF osf.io/b653h). Schéma : Pablo Correa Prieto.'],
        ),
        'items-exigence-cognitive': dict(
            kicker='Exigence cognitive · deux grilles publiées',
            title='Du rappel au raisonnement.',
            h1='Profondeur de connaissance', s1='Webb (1999)',
            l1=['Rappel', 'Habileté ou concept', 'Pensée stratégique', 'Pensée étendue'],
            h2='Exigence des tâches mathématiques', s2='Stein, Grover et Henningsen (1996)',
            l2=['Mémorisation', 'Procédures sans liens', 'Procédures avec liens', 'Faire des mathématiques'],
            axis='Exigence croissante',
            source=['Niveaux traduits par l’auteur. Sources : Webb (1999), Research Monograph No. 18 ; Stein, Grover et Henningsen (1996), American',
                    'Educational Research Journal, 33(2). « Procédures sans / avec liens » : sans / avec liens aux concepts. Schéma : Pablo Correa Prieto.'],
        ),
        'effort-ia-examen': dict(
            kicker='Apprendre · données publiées',
            title='Mieux réussir n’est pas mieux apprendre.',
            sub=['Écart de notes par rapport aux élèves sans IA, mathématiques, lycée (Bastani et al., 2025)'],
            leg1='Pendant les exercices, avec l’outil', leg2='À l’examen, sans l’outil',
            arm1='Accès libre à GPT-4', arm2='Tuteur GPT-4 : des indices, pas les réponses',
            r_practice='Pendant les exercices', r_exam='À l’examen',
            ns='différence non significative',
            zero='groupe sans IA',
            source=['Données : Bastani, H. et al. (2025). Generative AI without guardrails can harm learning. PNAS, 122(26), e2422633122.',
                    'Près de 1 000 élèves d’un lycée en Turquie. Graphique : Pablo Correa Prieto.'],
        ),
        'effort-garder-confier': dict(
            kicker='Apprendre · proposition',
            title='Où se trouve l’effort utile ?',
            h1='Garder exigeant', s1='L’effort est l’apprentissage visé',
            l1=['Se rappeler sans aide', 'Produire sa réponse avant de la vérifier', 'Expliquer avec ses mots', 'Faire un premier essai sur un problème'],
            h2='Confier à l’outil, sous contrôle', s2='L’effort n’est qu’un moyen',
            l2=['Mettre en forme', 'Générer des exercices d’entraînement en plus', 'Reformuler une consigne au bon niveau', 'Donner des indices plutôt que des réponses'],
            note='La même tâche peut changer de colonne selon l’objectif visé.',
            source=['Proposition de l’auteur, d’après Bjork et Bjork (2011) et Bastani et al. (2025). Schéma : Pablo Correa Prieto.'],
        ),
        'preparer-temps-gagne': dict(
            kicker='Préparer · données publiées',
            title='25 minutes de moins par semaine.',
            sub=['Temps hebdomadaire de préparation des leçons, enseignants de sciences, Angleterre'],
            r1=['Sans outil d’IA', '(groupe de comparaison)'], r2=['Avec ChatGPT', 'et un guide d’utilisation'],
            fmt=fr_min,
            diff='−25,3 min (−31 %)',
            quality=['Qualité des ressources : pas de différence constatée par un panel d’experts qui ignorait lesquelles avaient été faites avec ChatGPT.'],
            source=['Données : Roy, P. et al. (2024). ChatGPT in lesson preparation: A Teacher Choices trial. EEF / NFER. 259 enseignants, 68 écoles ;',
                    'temps déclaré par les enseignants. Graphique : Pablo Correa Prieto.'],
        ),
        'preparer-verifier': dict(
            kicker='Préparer · proposition',
            title='Le vrai travail : vérifier.',
            c1=('Générer', ['Quelques secondes :', 'exercices, variantes,', 'consignes.']),
            c2=('Vérifier', [['L’objectif du PER', 'en cours'], ['Le niveau d’exigence', 'pour la classe'], ['L’exactitude des', 'réponses et données']]),
            c3=('Adapter', ['À la classe et à ce', 'que le titulaire a', 'déjà construit.']),
            source=['Proposition de l’auteur, d’après le Plan d’études romand et les recommandations de la CIIP (2025). Schéma : Pablo Correa Prieto.'],
        ),
    },

    'en': {
        'detecteurs-exactitude': dict(
            kicker='Detection · published data',
            title='What detectors get right, and where they fail.',
            sub=['Mean accuracy of fourteen detection tools by document type, binary approach'],
            pct='{}%',
            rows=[('Human-written text', 94, 'blue'),
                  ('Machine-translated text', 69, 'blue'),
                  ('AI-generated text (set 1)', 63, 'blue'),
                  ('AI-generated text (set 2)', 70, 'blue'),
                  ('AI text edited by hand', 30, 'mark'),
                  ('AI text run through a paraphraser', 15, 'mark')],
            source=['Data: Weber-Wulff, D. et al. (2023). Testing of detection tools for AI-generated text.',
                    'International Journal for Educational Integrity, 19(1), 26. Chart: Pablo Correa Prieto.'],
        ),
        'detecteurs-decision': dict(
            kicker='Detection · analysis',
            title='A probability is not proof.',
            c1_label='What a detector produces',
            c1=['A probability', 'About a text', 'Without separating its', 'own mistakes'],
            c2_label='What a decision requires',
            c2=['Enough certainty', 'About a person', 'and about an act', 'That the student', 'can answer'],
            note=['Nothing in the tool\u2019s output separates',
                  'a correct flag from a mistaken one.'],
            source=['Author\u2019s analysis, drawing on Weber-Wulff et al. (2023), Van Vlasselaer et al. (2026) and the CIIP (2025)',
                    'recommendations. Diagram: Pablo Correa Prieto.'],
        ),
        'acceptation-correlations': dict(
            kicker='Measurement · published data',
            title='Correlations between self-reports.',
            sub=['What the correlations cited in support of acceptance models actually measure'],
            rows=[('Perceived usefulness ↔ self-predicted future use', 0.85, '.85',
                   ['Davis (1989). Two answers from the same person, in the same questionnaire.'], 'blue'),
                  ('Perceived usefulness ↔ self-reported use', 0.63, '.63',
                   ['Davis (1989). Also self-reported.'], 'blue'),
                  ('Self-reported use ↔ logged use', 0.38, '.38',
                   ['Parry et al. (2021). Meta-analysis of 44 studies, N = 52,007. Only 6% of mean self-reported',
                    'estimates fall within 5% of the logged mean.'], 'mark')],
            source=['Data: Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340; Parry, D. A. et al. (2021).',
                    'Nature Human Behaviour, 5(11), 1535–1547. Chart: Pablo Correa Prieto.'],
        ),
        'acceptation-chaine': dict(
            kicker='Measurement · analysis',
            title='Where validation stops.',
            sub=['From attitude to behaviour: what acceptance models actually cover'],
            boxes=[['Attitude'], ['Intention'], ['Self-reported use'], ['Logged use']],
            brace1=['what acceptance models validate'],
            brace2=['what we want', 'to know'],
            source=['Author\u2019s analysis, drawing on Davis (1989), Straub et al. (1995) and Parry et al. (2021).',
                    'Diagram: Pablo Correa Prieto.'],
        ),
        'feedback-information': dict(
            kicker='Feedback · published data',
            title='The effect follows the information.',
            sub=['Effect size of a response by what it contains (435 studies, k = 994)'],
            ref='overall effect 0.48',
            bars=[(['Reinforcement or punishment'], 0.24, '0.24'),
                  (['Corrective feedback'], 0.46, '0.46'),
                  (['High-information feedback'], 0.99, '0.99')],
            source=['Data: Wisniewski, B., Zierer, K. and Hattie, J. (2020). The power of feedback revisited.',
                    'Frontiers in Psychology, 10, 3087. Chart: Pablo Correa Prieto.'],
        ),
        'feedback-ia-expert': dict(
            kicker='Feedback · published data',
            title='Useful, but not enough to pass on.',
            sub=['Feedback judged useful for revision by 89 student teachers, blind to its source'],
            pct='{}%',
            rows=[(['Expert feedback,', 'judged useful for revision'], 88, 'blue'),
                  (['Language-model feedback,', 'judged useful for revision'], 59, 'blue'),
                  (['Model feedback the rater chooses', 'to pass on to the student'], 23, 'mark')],
            source=['Data: Jansen, T. et al. (2024). Comparing generative AI and expert feedback to students\u2019 writing.',
                    'Psychologie in Erziehung und Unterricht, 71(2), 80–92. Chart: Pablo Correa Prieto.'],
        ),
        'correction-meme-copie': dict(
            kicker='Assessment · published data',
            title='Same paper, 73 teachers.',
            sub=['Letter grades given to the same student essay'],
            stat1='50 to 96',
            stat1_label=['marks out of 100 given to this', 'same paper by 73 teachers'],
            stat2='A to F',
            stat2_label=['every letter on the scale,', 'for one and the same text'],
            source=['Data: Brimi, H. M. (2011). Reliability of grading high school work in English. Practical Assessment, Research & Evaluation, 16(17).',
                    'Chart: Pablo Correa Prieto.'],
        ),
        'correction-second-regard': dict(
            kicker='Assessment · proposal',
            title='A second reader, not a marker.',
            b1_label='Paper', b1=['Anonymised,', 'no name'],
            b2_label='Teacher', b2=['Marks it', 'as usual'],
            b3_label='AI, in parallel', b3=['Suggests a mark', 'or a comment'],
            b4_label='Compare', b4=['Do the two', 'marks agree?'],
            b5_label='Yes', b5=['The mark is', 'confirmed'],
            b6_label='No', b6=['The teacher', 'reviews, decides'],
            source=['After the parallel-marking set-up described by Ofqual (Williamson, 2026). The final decision stays with the teacher.',
                    'Diagram: Pablo Correa Prieto.'],
        ),
        'items-trois-questions': dict(
            kicker='Judging an item · three questions',
            title='Correct does not mean aligned.',
            c1=('Alignment', ['Does the item target the', 'stated PER objective?']),
            c2=('Cognitive demand', ['What level of thinking', 'does it really require?']),
            c3=('Quality', ['Is it correct, clear, clue-free,', 'with a single right answer?']),
            note='An item can pass one of these questions and fail the other two.',
            source=['Framework of Pablo Correa Prieto’s study in preparation (OSF project osf.io/b653h). Diagram: Pablo Correa Prieto.'],
        ),
        'items-exigence-cognitive': dict(
            kicker='Cognitive demand · two published frameworks',
            title='From recall to reasoning.',
            h1='Depth of knowledge', s1='Webb (1999)',
            l1=['Recall', 'Skill/concept', 'Strategic thinking', 'Extended thinking'],
            h2='Demands of mathematical tasks', s2='Stein, Grover and Henningsen (1996)',
            l2=['Memorisation', 'Procedures without connections', 'Procedures with connections', 'Doing mathematics'],
            axis='Increasing demand',
            source=['Sources: Webb (1999), Research Monograph No. 18; Stein, Grover & Henningsen (1996), American Educational Research Journal,',
                    '33(2). “Procedures without / with connections”: connections to concepts. Diagram: Pablo Correa Prieto.'],
        ),
        'effort-ia-examen': dict(
            kicker='Learning · published data',
            title='Doing better is not learning better.',
            sub=['Change in grades compared with students without AI, high-school mathematics (Bastani et al., 2025)'],
            leg1='During practice, with the tool', leg2='On the exam, without the tool',
            arm1='Open access to GPT-4', arm2='GPT-4 tutor: hints, not answers',
            r_practice='During practice', r_exam='On the exam',
            ns='no significant difference',
            zero='group without AI',
            source=['Data: Bastani, H. et al. (2025). Generative AI without guardrails can harm learning. PNAS, 122(26), e2422633122.',
                    'Nearly 1,000 students at a high school in Turkey. Chart: Pablo Correa Prieto.'],
        ),
        'effort-garder-confier': dict(
            kicker='Learning · proposal',
            title='Where is the useful effort?',
            h1='Keep demanding', s1='The effort is the learning itself',
            l1=['Recalling without help', 'Producing an answer before checking it', 'Explaining in one’s own words', 'A first attempt at a problem'],
            h2='Hand to the tool, under control', s2='The effort is only a means',
            l2=['Formatting', 'Generating extra practice exercises', 'Rewording instructions at the right level', 'Giving hints rather than answers'],
            note='The same task can switch columns depending on the objective.',
            source=['Author’s proposal, based on Bjork & Bjork (2011) and Bastani et al. (2025). Diagram: Pablo Correa Prieto.'],
        ),
        'preparer-temps-gagne': dict(
            kicker='Preparing · published data',
            title='25 minutes less per week.',
            sub=['Weekly lesson-preparation time, science teachers, England'],
            r1=['Without an AI tool', '(comparison group)'], r2=['With ChatGPT', 'and a user guide'],
            fmt=en_min,
            diff='−25.3 min (−31%)',
            quality=['Quality of resources: no difference found by an expert panel who did not know which ones had been made with ChatGPT.'],
            source=['Data: Roy, P. et al. (2024). ChatGPT in lesson preparation: A Teacher Choices trial. EEF / NFER. 259 teachers, 68 schools;',
                    'time self-reported by teachers. Chart: Pablo Correa Prieto.'],
        ),
        'preparer-verifier': dict(
            kicker='Preparing · proposal',
            title='The real work: checking.',
            c1=('Generate', ['A few seconds:', 'exercises, variants,', 'instructions.']),
            c2=('Check', [['The PER objective', 'being taught'], ['The level of demand', 'for the class'], ['Accuracy of the', 'answers and data']]),
            c3=('Adapt', ['To the class and to', 'what the regular', 'teacher has built.']),
            source=['Author’s proposal, based on the Plan d’études romand and the CIIP recommendations (2025). Diagram: Pablo Correa Prieto.'],
        ),
    },
    'es': {
        'detecteurs-exactitude': dict(
            kicker='Detección · datos publicados',
            title='Lo que los detectores aciertan, y dónde fallan.',
            sub=['Exactitud media de catorce herramientas de detección según el tipo de documento, enfoque binario'],
            pct='{} %',
            rows=[('Texto escrito por una persona', 94, 'blue'),
                  ('Texto traducido automáticamente', 69, 'blue'),
                  ('Texto generado por IA (serie 1)', 63, 'blue'),
                  ('Texto generado por IA (serie 2)', 70, 'blue'),
                  ('Texto de IA retocado a mano', 30, 'mark'),
                  ('Texto de IA pasado por un parafraseador', 15, 'mark')],
            source=['Datos: Weber-Wulff, D. et al. (2023). Testing of detection tools for AI-generated text.',
                    'International Journal for Educational Integrity, 19(1), 26. Gráfico: Pablo Correa Prieto.'],
        ),
        'detecteurs-decision': dict(
            kicker='Detección · análisis',
            title='Una probabilidad no es una prueba.',
            c1_label='Lo que produce un detector',
            c1=['Una probabilidad', 'Sobre un texto', 'Sin distinguir sus', 'propios errores'],
            c2_label='Lo que exige una decisión',
            c2=['Una certeza suficiente', 'Sobre una persona', 'y sobre un acto', 'A la que el alumno', 'pueda responder'],
            note=['Ninguna información en la salida de la herramienta',
                  'distingue el aviso acertado del aviso erróneo.'],
            source=['Análisis del autor, a partir de Weber-Wulff et al. (2023), Van Vlasselaer et al. (2026) y de las',
                    'recomendaciones de la CIIP (2025). Esquema: Pablo Correa Prieto.'],
        ),
        'acceptation-correlations': dict(
            kicker='Medición · datos publicados',
            title='Correlaciones entre declaraciones.',
            sub=['Lo que miden realmente las correlaciones citadas en apoyo de los modelos de aceptación'],
            rows=[('Utilidad percibida ↔ uso futuro autopredicho', 0.85, '0,85',
                   ['Davis (1989). Dos respuestas de la misma persona, en el mismo cuestionario.'], 'blue'),
                  ('Utilidad percibida ↔ uso declarado', 0.63, '0,63',
                   ['Davis (1989). También declarativo.'], 'blue'),
                  ('Uso declarado ↔ uso registrado', 0.38, '0,38',
                   ['Parry et al. (2021). Metaanálisis de 44 estudios, N = 52 007. Solo el 6 % de las estimaciones',
                    'declaradas medias quedan a menos del 5 % de la media registrada.'], 'mark')],
            source=['Datos: Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340; Parry, D. A. et al. (2021).',
                    'Nature Human Behaviour, 5(11), 1535–1547. Gráfico: Pablo Correa Prieto.'],
        ),
        'acceptation-chaine': dict(
            kicker='Medición · análisis',
            title='Dónde se detiene la validación.',
            sub=['De la actitud al comportamiento: lo que cubren realmente los modelos de aceptación'],
            boxes=[['Actitud'], ['Intención'], ['Uso declarado'], ['Uso registrado']],
            brace1=['lo que validan los modelos de aceptación'],
            brace2=['lo que queremos', 'saber'],
            source=['Análisis del autor, a partir de Davis (1989), Straub et al. (1995) y Parry et al. (2021).',
                    'Esquema: Pablo Correa Prieto.'],
        ),
        'feedback-information': dict(
            kicker='Feedback · datos publicados',
            title='El efecto sigue a la información.',
            sub=['Tamaño del efecto de una devolución según lo que contiene (435 estudios, k = 994)'],
            ref='efecto global 0,48',
            bars=[(['Reforzar o sancionar'], 0.24, '0,24'),
                  (['Devolución correctiva'], 0.46, '0,46'),
                  (['Devolución con mucha información'], 0.99, '0,99')],
            source=['Datos: Wisniewski, B., Zierer, K. y Hattie, J. (2020). The power of feedback revisited.',
                    'Frontiers in Psychology, 10, 3087. Gráfico: Pablo Correa Prieto.'],
        ),
        'feedback-ia-expert': dict(
            kicker='Feedback · datos publicados',
            title='Útil, pero no para transmitirlo.',
            sub=['Devoluciones juzgadas útiles para la revisión por 89 futuros docentes, sin conocer su origen'],
            pct='{} %',
            rows=[(['Devolución de un experto,', 'juzgada útil para la revisión'], 88, 'blue'),
                  (['Devolución de un modelo de lenguaje,', 'juzgada útil para la revisión'], 59, 'blue'),
                  (['Devolución del modelo que el evaluador', 'decide transmitir al alumno'], 23, 'mark')],
            source=['Datos: Jansen, T. et al. (2024). Comparing generative AI and expert feedback to students\u2019 writing.',
                    'Psychologie in Erziehung und Unterricht, 71(2), 80–92. Gráfico: Pablo Correa Prieto.'],
        ),
        'correction-meme-copie': dict(
            kicker='Evaluación · datos publicados',
            title='El mismo examen, 73 docentes.',
            sub=['Notas en letras que recibió la misma redacción de un alumno'],
            stat1='50 a 96',
            stat1_label=['notas sobre 100 que dieron', '73 docentes a este mismo examen'],
            stat2='A a F',
            stat2_label=['todas las letras de la escala', 'para un único y mismo texto'],
            source=['Datos: Brimi, H. M. (2011). Reliability of grading high school work in English. Practical Assessment, Research & Evaluation, 16(17).',
                    'Gráfico: Pablo Correa Prieto.'],
        ),
        'correction-second-regard': dict(
            kicker='Evaluación · propuesta',
            title='Una segunda mirada, no un corrector.',
            b1_label='Examen', b1=['Anonimizado,', 'sin nombre'],
            b2_label='Docente', b2=['Corrige', 'como siempre'],
            b3_label='IA, en paralelo', b3=['Propone una nota', 'o un comentario'],
            b4_label='Comparar', b4=['¿Coinciden', 'las dos?'],
            b5_label='Sí', b5=['La nota', 'se valida'],
            b6_label='No', b6=['El docente', 'revisa y decide'],
            source=['Según el dispositivo de puntuación en paralelo descrito por Ofqual (Williamson, 2026). La decisión final es del docente.',
                    'Esquema: Pablo Correa Prieto.'],
        ),
        'items-trois-questions': dict(
            kicker='Juzgar un ítem · tres preguntas',
            title='Correcto no significa alineado.',
            c1=('Alineación', ['¿Apunta el ítem al objetivo', 'del PER anunciado?']),
            c2=('Demanda cognitiva', ['¿Qué nivel de reflexión', 'pide realmente?']),
            c3=('Calidad', ['¿Es correcto, claro, sin pistas,', 'con una sola respuesta correcta?']),
            note='Un ítem puede superar una de estas preguntas y fallar las otras dos.',
            source=['Marco del estudio en preparación de Pablo Correa Prieto (proyecto OSF osf.io/b653h). Esquema: Pablo Correa Prieto.'],
        ),
        'items-exigence-cognitive': dict(
            kicker='Demanda cognitiva · dos marcos publicados',
            title='Del recuerdo al razonamiento.',
            h1='Profundidad de conocimiento', s1='Webb (1999)',
            l1=['Recuerdo', 'Habilidad o concepto', 'Pensamiento estratégico', 'Pensamiento extendido'],
            h2='Demanda de las tareas matemáticas', s2='Stein, Grover y Henningsen (1996)',
            l2=['Memorización', 'Procedimientos sin conexiones', 'Procedimientos con conexiones', 'Hacer matemáticas'],
            axis='Demanda creciente',
            source=['Niveles traducidos por el autor. Fuentes: Webb (1999), Research Monograph No. 18; Stein, Grover y Henningsen (1996), American',
                    'Educational Research Journal, 33(2). «Procedimientos sin / con conexiones»: con los conceptos. Esquema: Pablo Correa Prieto.'],
        ),
        'effort-ia-examen': dict(
            kicker='Aprender · datos publicados',
            title='Rendir más no es aprender más.',
            sub=['Diferencia de notas respecto a los alumnos sin IA, matemáticas en un instituto (Bastani et al., 2025)'],
            leg1='Durante los ejercicios, con la herramienta', leg2='En el examen, sin la herramienta', leg2x=640,
            arm1='Acceso libre a GPT-4', arm2='Tutor GPT-4: pistas, no respuestas',
            r_practice='Durante los ejercicios', r_exam='En el examen',
            ns='diferencia no significativa',
            zero='grupo sin IA',
            source=['Datos: Bastani, H. et al. (2025). Generative AI without guardrails can harm learning. PNAS, 122(26), e2422633122.',
                    'Cerca de 1000 alumnos de un instituto de Turquía. Gráfico: Pablo Correa Prieto.'],
        ),
        'effort-garder-confier': dict(
            kicker='Aprender · propuesta',
            title='¿Dónde está el esfuerzo útil?',
            h1='Mantener exigente', s1='El esfuerzo es el aprendizaje buscado',
            l1=['Recordar sin ayuda', 'Producir la respuesta antes de comprobarla', 'Explicar con las propias palabras', 'Hacer un primer intento ante un problema'],
            h2='Confiar a la herramienta, con control', s2='El esfuerzo es solo un medio',
            l2=['Dar formato', 'Generar ejercicios de práctica adicionales', 'Reformular una consigna al nivel adecuado', 'Dar pistas en lugar de respuestas'],
            note='La misma tarea puede cambiar de columna según el objetivo.',
            source=['Propuesta del autor, a partir de Bjork y Bjork (2011) y Bastani et al. (2025). Esquema: Pablo Correa Prieto.'],
        ),
        'preparer-temps-gagne': dict(
            kicker='Preparar · datos publicados',
            title='25 minutos menos por semana.',
            sub=['Tiempo semanal de preparación de clases, docentes de ciencias, Inglaterra'],
            r1=['Sin herramienta de IA', '(grupo de comparación)'], r2=['Con ChatGPT', 'y una guía de uso'],
            fmt=fr_min,
            diff='−25,3 min (−31 %)',
            quality=['Calidad de los recursos: sin diferencias según un panel de expertos que no sabía cuáles se habían hecho con ChatGPT.'],
            source=['Datos: Roy, P. et al. (2024). ChatGPT in lesson preparation: A Teacher Choices trial. EEF / NFER. 259 docentes, 68 centros;',
                    'tiempo declarado por los docentes. Gráfico: Pablo Correa Prieto.'],
        ),
        'preparer-verifier': dict(
            kicker='Preparar · propuesta',
            title='El verdadero trabajo: verificar.',
            c1=('Generar', ['Unos segundos:', 'ejercicios, variantes,', 'consignas.']),
            c2=('Verificar', [['El objetivo del PER', 'en curso'], ['El nivel de exigencia', 'para la clase'], ['La exactitud de', 'respuestas y datos']]),
            c3=('Adaptar', ['A la clase y a lo', 'que el titular ya', 'ha construido.']),
            source=['Propuesta del autor, a partir del Plan d’études romand y de las recomendaciones de la CIIP (2025). Esquema: Pablo Correa Prieto.'],
        ),
    },
}


# ---------------------------------------------------------------- programme figures (Oct 2026)
# Figures for the research programme, the Swiss-texts reference page and the
# training page (not tied to one article). Conceptual diagrams only.

def _numcol(x, head, rows, num=None, head_size=44, y_rule=300):
    """Column in the style of fig_three_questions: rule, serif number/figure, serif head, sans rows."""
    b = [f'<line x1="{x}" y1="{y_rule}" x2="{x + 484}" y2="{y_rule}" stroke="{C["rule"]}" stroke-width="2"/>']
    if num:
        b.append(f'<text class="serif" x="{x}" y="{y_rule + 98}" font-family="{SERIF}" font-size="60" font-weight="400" fill="{C["mark"]}" data-maxw="484">{escape(num)}</text>')
    b.append(f'<text class="serif" x="{x}" y="{y_rule + 178}" font-family="{SERIF}" font-size="{head_size}" font-weight="500" fill="{C["ink"]}" data-maxw="484">{escape(head)}</text>')
    b.append(lines(x, y_rule + 232, rows, size=28, fill=C['muted'], maxw=484))
    return '\n'.join(b)


def fig_p_identity(lang, T):
    """Presentation card: name as the headline, the three research themes, credentials from the site."""
    b = []
    for i, (x, head, rows) in enumerate([(L, T['a1'][0], T['a1'][1]),
                                         (L + 543, T['a2'][0], T['a2'][1]),
                                         (L + 1086, T['a3'][0], T['a3'][1])]):
        b.append(_numcol(x, head, rows, num=f'0{i + 1}', head_size=40, y_rule=310))
    b.append(t(L, 712, escape(T['facts']), size=27, weight=500, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), None, title_size=92)


def fig_p_programme(lang, T):
    """The research programme in three strands."""
    b = []
    for i, (x, (head, rows)) in enumerate([(L, T['c1']), (L + 543, T['c2']), (L + 1086, T['c3'])]):
        b.append(_numcol(x, head, rows, num=f'0{i + 1}'))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_llm_per(lang, T):
    """Article 1 in one view: PER objectives, LLM-generated items, three judgements."""
    b = []
    b.append(box(L, 380, 430, 190, T['b1_label'], T['b1']))
    b.append(box(665, 380, 430, 190, T['b2_label'], T['b2']))
    b.append(box(1230, 320, 455, 310, T['b3_label'], T['b3'], emph=True))
    b.append(lines(1260, 596, T['b3_note'], size=23, fill=C['muted'], maxw=395))
    b.append(arrow(L + 430 + 8, 475, 657, 475))
    b.append(arrow(1095 + 8, 475, 1222, 475))
    b.append(lines(L, 710, T['note'], size=28, weight=500, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_wpr(lang, T):
    """Article 2 in one view: a corpus of official texts read with Bacchi's WPR approach."""
    b = []
    b.append(box(L, 350, 470, 250, T['b1_label'], T['b1']))
    b.append(lines(L + 30, 520, T['b1_note'], size=23, fill=C['muted'], maxw=410))
    b.append(box(705, 350, 430, 250, T['b2_label'], T['b2']))
    b.append(lines(735, 520, T['b2_note'], size=23, fill=C['muted'], maxw=370))
    b.append(box(1250, 350, 435, 250, T['b3_label'], T['b3'], emph=True, size=32))
    b.append(arrow(L + 470 + 8, 475, 697, 475))
    b.append(arrow(1135 + 8, 475, 1242, 475))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_niveaux(lang, T):
    """Who frames AI for schools: four levels of public texts, national to classroom."""
    b = []
    y = 288
    for i, (name, tag, desc) in enumerate(T['rows']):
        x, w = L + i * 56, R - L - 3 * 56
        b.append(rrect(x, y, w, 88, fill=C['white'], stroke=C['rule']))
        b.append(f'<rect x="{x}" y="{y}" width="8" height="88" rx="3" fill="{C["blue"]}"/>')
        b.append(f'<text class="serif" x="{x + 36}" y="{y + 46}" font-family="{SERIF}" font-size="34" font-weight="500" fill="{C["ink"]}" data-maxw="330">{escape(name)}</text>')
        b.append(t(x + 36, y + 74, escape(tag.upper()), size=17, weight=600, fill=C['accent'], ls='2', maxw=330))
        b.append(lines(x + 410, y + 54, [desc], size=25, fill=C['muted'], maxw=w - 440))
        if i < 3:
            b.append(arrow(x + 90, y + 90, x + 90 + 40, y + 110))
        y += 112
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_grappes(lang, T):
    """Planned study design: whole schools randomised to a short training or usual practice."""
    b = []
    b.append(box(L, 390, 360, 270, T['b1_label'], T['b1'], size=30))
    for i in range(2):
        for j in range(5):
            b.append(rrect(L + 32 + j * 58, 535 + i * 58, 44, 44, r=8,
                           fill=C['soft'], stroke=C['blue'], sw=2))
    b.append(box(615, 330, 480, 140, T['b2_label'], T['b2'], emph=True, size=30))
    b.append(box(615, 530, 480, 140, T['b3_label'], T['b3'], size=30))
    b.append(box(1230, 420, 455, 190, T['b4_label'], T['b4'], size=32))
    b.append(elbow(L + 360 + 6, 470, 607, 400))
    b.append(elbow(L + 360 + 6, 560, 607, 600))
    b.append(elbow(1095 + 6, 400, 1222, 500))
    b.append(elbow(1095 + 6, 600, 1222, 530))
    b.append(lines(L, 712, T['note'], size=28, weight=500, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_tam(lang, T):
    """The technology acceptance model (Davis, 1989), as used in the planned teacher study."""
    b = []
    b.append(box(L, 320, 430, 150, T['b1_label'], T['b1'], size=32))
    b.append(box(L, 540, 430, 150, T['b2_label'], T['b2'], size=32))
    b.append(box(700, 430, 420, 150, T['b3_label'], T['b3'], size=32))
    b.append(box(1265, 430, 420, 150, T['b4_label'], T['b4'], emph=True, size=32))
    b.append(elbow(L + 430 + 6, 395, 692, 480))
    b.append(elbow(L + 430 + 6, 615, 692, 530))
    b.append(arrow(1120 + 6, 505, 1257, 505))
    b.append(lines(L, 745, T['note'], size=26, fill=C['muted'], maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_formations(lang, T):
    """The three training formats for school teams."""
    b = []
    for x, (num, head, rows) in [(L, T['c1']), (L + 543, T['c2']), (L + 1086, T['c3'])]:
        b.append(_numcol(x, head, rows, num=num))
    b.append(t(L, 712, escape(T['note']), size=28, weight=500, maxw=R - L))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_questions(lang, T):
    """Four questions to ask before using AI in class."""
    b = []
    y = 282
    for i, (word, q) in enumerate(T['rows']):
        b.append(rrect(L, y, R - L, 92, fill=C['white'], stroke=C['rule']))
        b.append(f'<text class="serif" x="{L + 38}" y="{y + 60}" font-family="{SERIF}" font-size="40" font-weight="400" fill="{C["mark"]}">{i + 1}</text>')
        b.append(f'<text class="serif" x="{L + 100}" y="{y + 58}" font-family="{SERIF}" font-size="33" font-weight="500" fill="{C["ink"]}" data-maxw="300">{escape(word)}</text>')
        b.append(lines(L + 470, y + 56, [q], size=26, fill=C['muted'], maxw=R - L - 510))
        y += 110
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


def fig_p_methodes(lang, T):
    """The methods used across the programme, one box each."""
    b = []
    for i, (head, rows) in enumerate(T['cells']):
        x = L + (i % 2) * 800
        y = 290 + (i // 2) * 230
        b.append(rrect(x, y, 770, 200, fill=C['white'], stroke=C['rule']))
        b.append(f'<rect x="{x}" y="{y}" width="8" height="200" rx="3" fill="{C["blue"]}"/>')
        b.append(f'<text class="serif" x="{x + 36}" y="{y + 62}" font-family="{SERIF}" font-size="36" font-weight="500" fill="{C["ink"]}" data-maxw="700">{escape(head)}</text>')
        b.append(lines(x + 36, y + 110, rows, size=25, fill=C['muted'], maxw=700))
    return frame(T['lang'], T['kicker'], T['title'], '\n'.join(b), T['source'])


FIGS.update({
    'chercheur-ia-education': fig_p_identity,
    'programme-recherche': fig_p_programme,
    'recherche-items-llm': fig_p_llm_per,
    'politiques-corpus-wpr': fig_p_wpr,
    'politiques-niveaux': fig_p_niveaux,
    'recherche-essai-grappes': fig_p_grappes,
    'acceptation-modele-tam': fig_p_tam,
    'formations-formats': fig_p_formations,
    'ia-classe-quatre-questions': fig_p_questions,
    'methodes-recherche': fig_p_methodes,
})

TEXT['fr'].update({
    'chercheur-ia-education': dict(
        kicker='Enseignant et chercheur · canton de Vaud',
        title='Pablo Correa Prieto.',
        a1=('Évaluation et IA', ['Items d’évaluation générés', 'par IA, jugés au regard', 'du Plan d’études romand.']),
        a2=('Acceptation enseignante', ['Ce qui conduit les enseignants', 'à utiliser, ou non, l’IA', 'générative en classe.']),
        a3=('Politiques publiques', ['Comment les textes officiels', 'romands cadrent l’IA', 'à l’école obligatoire.']),
        facts='Reconnaissance CDIP 3H–8H · Master en méthodes de recherche en éducation (UNIR) · ORCID 0009-0009-1844-7453',
    ),
    'programme-recherche': dict(
        kicker='Recherche · programme',
        title='Un programme, trois axes.',
        c1=('Évaluation', ['Des items générés par IA,', 'jugés au regard du PER :', 'alignement, exigence', 'cognitive, qualité.']),
        c2=('Acceptation', ['L’intention d’usage de l’IA', 'générative chez les', 'enseignants, et ce qu’une', 'formation courte y change.']),
        c3=('Politiques', ['Comment les textes officiels', 'romands représentent le', '« problème » de l’IA', 'à l’école.']),
        source=['Programme de recherche de l’auteur. Schéma : Pablo Correa Prieto.'],
    ),
    'recherche-items-llm': dict(
        kicker='Recherche · article en préparation',
        title='Des items générés, trois jugements.',
        b1_label='Plan d’études', b1=['Objectifs du PER,', 'mathématiques'],
        b2_label='Génération', b2=['Items produits', 'par un LLM'],
        b3_label='Trois jugements', b3=['Alignement', 'Exigence cognitive', 'Qualité'],
        b3_note=[],
        note=['Un item juste n’est pas forcément aligné : les trois jugements sont distincts.'],
        source=['Article en préparation ; les trois critères sont présentés dans l’article « Trois questions pour juger un item ».',
                'Schéma : Pablo Correa Prieto.'],
    ),
    'politiques-corpus-wpr': dict(
        kicker='Politiques · article en préparation',
        title='Ce que les textes font dire à l’IA.',
        b1_label='Corpus', b1=['Textes officiels', 'romands'],
        b1_note=['Recommandations, cadres', 'et directives sur l’IA', 'à l’école obligatoire.'],
        b2_label='Lecture', b2=['Approche WPR'],
        b2_note=['« What’s the problem', 'represented to be? »', '(Bacchi, 2009).'],
        b3_label='Question', b3=['Quel « problème »', 'ces textes', 'construisent-ils ?'],
        source=['Approche d’après Bacchi, C. (2009). Analysing Policy: What’s the problem represented to be? Pearson Australia.',
                'Article en préparation. Schéma : Pablo Correa Prieto.'],
    ),
    'politiques-niveaux': dict(
        kicker='Politiques · repères',
        title='Qui encadre l’IA à l’école.',
        rows=[('CDIP', 'Coordination nationale', 'Orientations pour l’ensemble des cantons suisses'),
              ('CIIP', 'Suisse romande et Tessin', 'Recommandations communes pour la scolarité obligatoire'),
              ('Cantons', 'Directives', 'Cadres d’usage et consignes aux établissements'),
              ('Écoles et HEP', 'Mise en œuvre', 'Chartes, formation des enseignants, pratique de classe')],
        source=['Analyse de l’auteur, à partir des textes publics de la CDIP, de la CIIP et des cantons romands.',
                'Schéma : Pablo Correa Prieto.'],
    ),
    'recherche-essai-grappes': dict(
        kicker='Méthode · étude en préparation',
        title='Randomiser des écoles, pas des personnes.',
        b1_label='Établissements', b1=['Écoles tirées', 'au sort'],
        b2_label='Groupe formation', b2=['Formation courte à', 'l’IA générative'],
        b3_label='Groupe témoin', b3=['Pratique habituelle,', 'sans formation'],
        b4_label='Mesure', b4=['Intention d’usage', 'de l’IA générative'],
        note=['Randomiser l’établissement entier évite qu’un enseignant formé influence un collègue du groupe témoin.'],
        source=['Étude en préparation, enseignants primaires du canton de Vaud. Schéma : Pablo Correa Prieto.'],
    ),
    'acceptation-modele-tam': dict(
        kicker='Acceptation · cadre théorique',
        title='Le modèle derrière les enquêtes.',
        b1_label='Croyance', b1=['Utilité perçue', 'pour enseigner'],
        b2_label='Croyance', b2=['Facilité d’usage', 'perçue'],
        b3_label='Attitude', b3=['Attitude envers', 'l’IA générative'],
        b4_label='Construit mesuré', b4=['Intention', 'd’usage'],
        note=['Ce que ces enquêtes mesurent, et où s’arrête leur validation : voir l’article « L’acceptation n’est pas l’usage ».'],
        source=['D’après Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340. Schéma : Pablo Correa Prieto.'],
    ),
    'formations-formats': dict(
        kicker='Formations · établissements',
        title='Trois formats, un même terrain.',
        c1=('90 min', 'Conférence-atelier', ['Comprendre ce que l’IA', 'générative change pour', 'préparer, évaluer et', 'faire apprendre.']),
        c2=('½ journée', 'Atelier pratique', ['Prendre en main les outils', 'sur ses propres séquences,', 'avec des cas tirés', 'du terrain vaudois.']),
        c3=('3 séances', 'Parcours d’équipe', ['Aboutir à une charte', 'd’usage de l’IA propre', 'à l’établissement, portée', 'par l’équipe.']),
        note='Aucun outil à vendre : les contenus viennent du terrain et des travaux présentés sur ce site.',
        source=['Offre de formation de l’auteur, détaillée sur pablocorreaprieto.ch/formations. Schéma : Pablo Correa Prieto.'],
    ),
    'ia-classe-quatre-questions': dict(
        kicker='Repères pour la classe · proposition',
        title='Quatre questions avant d’utiliser l’IA.',
        rows=[('Données', 'Des données d’élèves sortent-elles de l’école ? Si oui, on s’arrête là.'),
              ('Alignement', 'La tâche sert-elle un objectif du PER, ou seulement la nouveauté de l’outil ?'),
              ('Effort', 'L’effort qui fait apprendre reste-t-il chez l’élève, ou passe-t-il à la machine ?'),
              ('Transparence', 'Élèves et parents savent-ils quand et comment l’IA a été utilisée ?')],
        source=['Proposition de l’auteur, à partir des recommandations de la CIIP (2025) et des travaux cités dans les articles de ce site.',
                'Schéma : Pablo Correa Prieto.'],
    ),
    'methodes-recherche': dict(
        kicker='Recherche · méthodes',
        title='Des méthodes au service des questions.',
        cells=[('Analyse documentaire', ['Corpus de textes officiels, cadre WPR,', 'second codage indépendant.']),
               ('Essai randomisé en grappes', ['Écoles entières tirées au sort, groupe', 'témoin, effet d’une formation.']),
               ('Échelles et questionnaires', ['Attitude et intention d’usage,', 'fiabilité des instruments.']),
               ('Jugement d’items', ['Alignement curriculaire, exigence', 'cognitive et qualité d’items générés.'])],
        source=['Méthodes mobilisées dans les travaux de l’auteur. Schéma : Pablo Correa Prieto.'],
    ),
})

TEXT['en'].update({
    'chercheur-ia-education': dict(
        kicker='Teacher and researcher · canton of Vaud',
        title='Pablo Correa Prieto.',
        a1=('Assessment and AI', ['AI-generated assessment', 'items, judged against the', 'Plan d’études romand.']),
        a2=('Teacher acceptance', ['What leads teachers to use,', 'or not use, generative AI', 'in the classroom.']),
        a3=('Public policy', ['How official texts in French-', 'speaking Switzerland frame', 'AI for compulsory school.']),
        facts='CDIP recognition, years 3H–8H · Master’s in education research methods (UNIR) · ORCID 0009-0009-1844-7453',
    ),
    'programme-recherche': dict(
        kicker='Research · programme',
        title='One programme, three strands.',
        c1=('Assessment', ['AI-generated items, judged', 'against the curriculum:', 'alignment, cognitive', 'demand, quality.']),
        c2=('Acceptance', ['Teachers’ intention to use', 'generative AI, and what', 'a short training', 'changes about it.']),
        c3=('Policy', ['How official texts in French-', 'speaking Switzerland', 'represent the “problem”', 'of AI in schools.']),
        source=['The author’s research programme. Diagram: Pablo Correa Prieto.'],
    ),
    'recherche-items-llm': dict(
        kicker='Research · article in preparation',
        title='Generated items, three judgements.',
        b1_label='Curriculum', b1=['Objectives of the PER,', 'mathematics'],
        b2_label='Generation', b2=['Items produced', 'by an LLM'],
        b3_label='Three judgements', b3=['Alignment', 'Cognitive demand', 'Quality'],
        b3_note=[],
        note=['A correct item is not necessarily aligned: the three judgements are distinct.'],
        source=['Article in preparation; the three criteria are presented in “Three questions for judging an item”.',
                'Diagram: Pablo Correa Prieto.'],
    ),
    'politiques-corpus-wpr': dict(
        kicker='Policy · article in preparation',
        title='What the official texts make AI mean.',
        b1_label='Corpus', b1=['Official texts,', 'French-speaking', 'Switzerland'],
        b1_note=['Recommendations, frameworks', 'and directives on AI', 'in compulsory school.'],
        b2_label='Reading', b2=['WPR approach'],
        b2_note=['“What’s the problem', 'represented to be?”', '(Bacchi, 2009).'],
        b3_label='Question', b3=['What “problem”', 'do these texts', 'construct?'],
        source=['Approach after Bacchi, C. (2009). Analysing Policy: What’s the problem represented to be? Pearson Australia.',
                'Article in preparation. Diagram: Pablo Correa Prieto.'],
    ),
    'politiques-niveaux': dict(
        kicker='Policy · reference',
        title='Who frames AI for schools.',
        rows=[('CDIP', 'National coordination', 'Shared orientations for all the Swiss cantons'),
              ('CIIP', 'Romandie and Ticino', 'Common recommendations for compulsory schooling'),
              ('Cantons', 'Directives', 'Usage frameworks and instructions to schools'),
              ('Schools and HEP', 'Implementation', 'School charters, teacher training, classroom practice')],
        source=['The author’s analysis, based on the public texts of the CDIP, the CIIP and the cantons.',
                'Diagram: Pablo Correa Prieto.'],
    ),
    'recherche-essai-grappes': dict(
        kicker='Method · study in preparation',
        title='Randomise schools, not people.',
        b1_label='Schools', b1=['Whole schools', 'drawn at random'],
        b2_label='Training arm', b2=['Short training in', 'generative AI'],
        b3_label='Control arm', b3=['Usual practice,', 'no training'],
        b4_label='Measure', b4=['Intention to use', 'generative AI'],
        note=['Randomising the whole school keeps a trained teacher from influencing a colleague in the control arm.'],
        source=['Study in preparation, primary teachers in the canton of Vaud. Diagram: Pablo Correa Prieto.'],
    ),
    'acceptation-modele-tam': dict(
        kicker='Acceptance · theoretical frame',
        title='The model behind the surveys.',
        b1_label='Belief', b1=['Perceived usefulness', 'for teaching'],
        b2_label='Belief', b2=['Perceived', 'ease of use'],
        b3_label='Attitude', b3=['Attitude towards', 'generative AI'],
        b4_label='Measured construct', b4=['Intention', 'to use'],
        note=['What these surveys measure, and where their validation stops: see “Acceptance is not use”.'],
        source=['After Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340. Diagram: Pablo Correa Prieto.'],
    ),
    'formations-formats': dict(
        kicker='Training · school teams',
        title='Three formats, one classroom base.',
        c1=('90 min', 'Talk and workshop', ['Understand what generative', 'AI changes for preparing,', 'assessing and helping', 'pupils learn.']),
        c2=('Half day', 'Hands-on workshop', ['Work on your own teaching', 'sequences, with cases', 'drawn from Vaud', 'classrooms.']),
        c3=('3 sessions', 'Team pathway', ['End with an AI-use charter', 'of the school’s own,', 'carried by the team.']),
        note='Nothing to sell: the content comes from the classroom and from the work presented on this site.',
        source=['The author’s training offer, detailed at pablocorreaprieto.ch/en/training. Diagram: Pablo Correa Prieto.'],
    ),
    'ia-classe-quatre-questions': dict(
        kicker='Classroom reference · proposal',
        title='Four questions before using AI.',
        rows=[('Data', 'Does any pupil data leave the school? If so, stop there.'),
              ('Alignment', 'Does the task serve a curriculum objective, or only the novelty of the tool?'),
              ('Effort', 'Does the effort that drives learning stay with the pupil, or move to the machine?'),
              ('Transparency', 'Do pupils and parents know when and how AI was used?')],
        source=['The author’s proposal, based on the CIIP recommendations (2025) and the work cited in this site’s articles.',
                'Diagram: Pablo Correa Prieto.'],
    ),
    'methodes-recherche': dict(
        kicker='Research · methods',
        title='Methods in the service of questions.',
        cells=[('Document analysis', ['A corpus of official texts, the WPR frame,', 'independent second coding.']),
               ('Cluster-randomised trial', ['Whole schools drawn at random, a control', 'arm, the effect of a training.']),
               ('Scales and questionnaires', ['Attitude and intention to use,', 'reliability of the instruments.']),
               ('Item judgement', ['Curricular alignment, cognitive demand', 'and quality of generated items.'])],
        source=['Methods used across the author’s work. Diagram: Pablo Correa Prieto.'],
    ),
})

TEXT['es'].update({
    'chercheur-ia-education': dict(
        kicker='Docente e investigador · cantón de Vaud',
        title='Pablo Correa Prieto.',
        a1=('Evaluación e IA', ['Ítems de evaluación generados', 'por IA, juzgados según el', 'Plan d’études romand.']),
        a2=('Aceptación docente', ['Qué lleva al profesorado a', 'usar, o no, la IA generativa', 'en el aula.']),
        a3=('Políticas públicas', ['Cómo los textos oficiales', 'de la Suiza francófona', 'encuadran la IA escolar.']),
        facts='Reconocimiento CDIP 3H–8H · Máster en métodos de investigación educativa (UNIR) · ORCID 0009-0009-1844-7453',
    ),
    'programme-recherche': dict(
        kicker='Investigación · programa',
        title='Un programa, tres ejes.',
        c1=('Evaluación', ['Ítems generados por IA,', 'juzgados según el currículo:', 'alineación, exigencia', 'cognitiva, calidad.']),
        c2=('Aceptación', ['La intención de uso de la IA', 'generativa en el profesorado,', 'y qué cambia una', 'formación breve.']),
        c3=('Políticas', ['Cómo los textos oficiales', 'de la Suiza francófona', 'representan el «problema»', 'de la IA escolar.']),
        source=['Programa de investigación del autor. Esquema: Pablo Correa Prieto.'],
    ),
    'recherche-items-llm': dict(
        kicker='Investigación · artículo en preparación',
        title='Ítems generados, tres juicios.',
        b1_label='Currículo', b1=['Objetivos del PER,', 'matemáticas'],
        b2_label='Generación', b2=['Ítems producidos', 'por un LLM'],
        b3_label='Tres juicios', b3=['Alineación', 'Exigencia cognitiva', 'Calidad'],
        b3_note=[],
        note=['Un ítem correcto no está necesariamente alineado: los tres juicios son distintos.'],
        source=['Artículo en preparación; los tres criterios se presentan en «Tres preguntas para juzgar un ítem».',
                'Esquema: Pablo Correa Prieto.'],
    ),
    'politiques-corpus-wpr': dict(
        kicker='Políticas · artículo en preparación',
        title='Lo que los textos hacen decir a la IA.',
        b1_label='Corpus', b1=['Textos oficiales,', 'Suiza francófona'],
        b1_note=['Recomendaciones, marcos', 'y directivas sobre la IA', 'en la escuela obligatoria.'],
        b2_label='Lectura', b2=['Enfoque WPR'],
        b2_note=['«What’s the problem', 'represented to be?»', '(Bacchi, 2009).'],
        b3_label='Pregunta', b3=['¿Qué «problema»', 'construyen', 'estos textos?'],
        source=['Enfoque según Bacchi, C. (2009). Analysing Policy: What’s the problem represented to be? Pearson Australia.',
                'Artículo en preparación. Esquema: Pablo Correa Prieto.'],
    ),
    'politiques-niveaux': dict(
        kicker='Políticas · referencia',
        title='Quién encuadra la IA escolar.',
        rows=[('CDIP', 'Coordinación nacional', 'Orientaciones para el conjunto de los cantones suizos'),
              ('CIIP', 'Suiza francófona y Tesino', 'Recomendaciones comunes para la escuela obligatoria'),
              ('Cantones', 'Directivas', 'Marcos de uso e instrucciones a los centros'),
              ('Centros y HEP', 'Aplicación', 'Cartas de centro, formación docente, práctica de aula')],
        source=['Análisis del autor, a partir de los textos públicos de la CDIP, la CIIP y los cantones.',
                'Esquema: Pablo Correa Prieto.'],
    ),
    'recherche-essai-grappes': dict(
        kicker='Método · estudio en preparación',
        title='Aleatorizar escuelas, no personas.',
        b1_label='Centros', b1=['Escuelas enteras', 'sorteadas'],
        b2_label='Grupo formación', b2=['Formación breve en', 'IA generativa'],
        b3_label='Grupo de control', b3=['Práctica habitual,', 'sin formación'],
        b4_label='Medida', b4=['Intención de uso', 'de la IA generativa'],
        note=['Aleatorizar el centro entero evita que un docente formado influya en un colega del grupo de control.'],
        source=['Estudio en preparación, docentes de primaria del cantón de Vaud. Esquema: Pablo Correa Prieto.'],
    ),
    'acceptation-modele-tam': dict(
        kicker='Aceptación · marco teórico',
        title='El modelo detrás de las encuestas.',
        b1_label='Creencia', b1=['Utilidad percibida', 'para enseñar'],
        b2_label='Creencia', b2=['Facilidad de uso', 'percibida'],
        b3_label='Actitud', b3=['Actitud hacia', 'la IA generativa'],
        b4_label='Constructo medido', b4=['Intención', 'de uso'],
        note=['Qué miden estas encuestas y dónde se detiene su validación: véase «La aceptación no es el uso».'],
        source=['Según Davis, F. D. (1989). MIS Quarterly, 13(3), 319–340. Esquema: Pablo Correa Prieto.'],
    ),
    'formations-formats': dict(
        kicker='Formaciones · equipos docentes',
        title='Tres formatos, un mismo terreno.',
        c1=('90 min', 'Conferencia-taller', ['Entender qué cambia la IA', 'generativa para preparar,', 'evaluar y hacer', 'aprender.']),
        c2=('½ jornada', 'Taller práctico', ['Trabajar sobre las propias', 'secuencias, con casos', 'tomados de las aulas', 'del cantón de Vaud.']),
        c3=('3 sesiones', 'Itinerario de equipo', ['Terminar con una carta de', 'uso de la IA propia del', 'centro, asumida por', 'el equipo.']),
        note='Nada que vender: los contenidos vienen del aula y de los trabajos presentados en este sitio.',
        source=['Oferta de formación del autor, detallada en pablocorreaprieto.ch/es/formaciones. Esquema: Pablo Correa Prieto.'],
    ),
    'ia-classe-quatre-questions': dict(
        kicker='Referencias para el aula · propuesta',
        title='Cuatro preguntas antes de usar la IA.',
        rows=[('Datos', '¿Salen datos del alumnado fuera de la escuela? Si es así, ahí se acaba.'),
              ('Alineación', '¿Sirve la tarea a un objetivo del currículo, o solo a la novedad de la herramienta?'),
              ('Esfuerzo', '¿El esfuerzo que hace aprender queda en el alumno, o pasa a la máquina?'),
              ('Transparencia', '¿Saben alumnos y familias cuándo y cómo se usó la IA?')],
        source=['Propuesta del autor, a partir de las recomendaciones de la CIIP (2025) y de los trabajos citados en los artículos.',
                'Esquema: Pablo Correa Prieto.'],
    ),
    'methodes-recherche': dict(
        kicker='Investigación · métodos',
        title='Métodos al servicio de las preguntas.',
        cells=[('Análisis documental', ['Corpus de textos oficiales, marco WPR,', 'segunda codificación independiente.']),
               ('Ensayo aleatorizado por conglomerados', ['Escuelas enteras sorteadas, grupo de', 'control, efecto de una formación.']),
               ('Escalas y cuestionarios', ['Actitud e intención de uso,', 'fiabilidad de los instrumentos.']),
               ('Juicio de ítems', ['Alineación curricular, exigencia', 'cognitiva y calidad de ítems generados.'])],
        source=['Métodos empleados en los trabajos del autor. Esquema: Pablo Correa Prieto.'],
    ),
})


def main():
    os.makedirs(OUT, exist_ok=True)
    for lang, figs in TEXT.items():
        for key, T in figs.items():
            T = dict(T, lang=lang)
            svg = FIGS[key](lang, T)
            path = os.path.join(OUT, f'pablo-correa-prieto-{key}-{lang}.svg')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(svg)
            print('wrote', os.path.relpath(path))


if __name__ == '__main__':
    main()
