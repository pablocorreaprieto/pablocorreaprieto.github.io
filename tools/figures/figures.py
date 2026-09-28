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


FIGS = {
    'correction-meme-copie': fig_meme_copie,
    'correction-second-regard': fig_second_regard,
    'items-trois-questions': fig_three_questions,
    'items-exigence-cognitive': fig_levels,
    'effort-ia-examen': fig_ia_examen,
    'effort-garder-confier': fig_garder_confier,
    'preparer-temps-gagne': fig_temps_gagne,
    'preparer-verifier': fig_verifier,
}


def fr_min(v):
    return f'{v:.1f}'.replace('.', ',') + ' min'


def en_min(v):
    return f'{v:.1f} min'


TEXT = {
    'fr': {
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
