#!/usr/bin/env python3
"""Genera el sitio estático de la travesía del velero Cabo de Hornos a Malvinas.

Uso: python scripts/build_site.py

Lee data/track.js (generado por build_track.py) para las millas de cada capítulo.
Las fotos y videos se toman de assets/; si un archivo todavía no está, la página
muestra un recuadro "pendiente" con el nombre esperado, para ubicarlo después.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = True  # muestra avisos de borrador; pasar a False antes de publicar
SITE = "Cabo de Hornos a Malvinas"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

NAV = [
    ("Inicio", "index.html"),
    ("Bitácora", "pages/bitacora/index.html"),
    ("Cartografía", "cartografia.html"),
    ("Homenaje al Sobral", "pages/sobral.html"),
    ("Videos", "pages/videos.html"),
    ("Galería", "pages/gallery.html"),
    ("El velero", "pages/velero.html"),
]

STAGES = [
    ("Rumbo al sur", "Del Río de la Plata a la costa patagónica, esperando la ventana para cruzar.", 0, 4),
    ("Malvinas", "El cruce, el homenaje al ARA «Alférez Sobral», Puerto Argentino y la vuelta al continente.", 4, 9),
    ("El regreso", "San Julián, el golfo San Jorge, Valdés y la subida final hasta Núñez.", 9, 13),
]


def q(text, cite):
    """Cita textual de un mensaje del inReach."""
    return (f'<blockquote class="inreach-quote">{html.escape(text)}'
            f'<cite>Mensaje enviado por inReach · {html.escape(cite)}</cite></blockquote>')


def p(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


# Cada capítulo: slug, título, desde, hasta, bajada, cuerpo (HTML) y medios sugeridos.
CHAPTERS = [
    dict(slug="la-zarpada", title="La zarpada y el Río de la Plata", start=date(2024, 1, 2), end=date(2024, 1, 5),
         lead="De Núñez a Mar del Plata, con viento y ola de proa desde la primera noche.",
         body=p("El Cabo de Hornos dejó Núñez la tarde del 2 de enero de 2024, más tarde de lo previsto. La primera prueba del inReach salió frente a Punta Lara, con 16 nudos del ENE y bastante ola «de jeta»: a motor y sin velas.",
                "La primera noche ya mostró el carácter del río: 25 nudos del este, rizo tres y trinquetilla, tirando bordes para pasar Magdalena. Al amanecer del 4, virando Punta Piedras, la tripulación pudo relajarse un poco.")
         + q("Estamo con R3 y rinquetilla. Mucha ola para motor. Tirando bordes... acá 25 nudos del este. Pasando magdalena", "4 de enero, frente a Magdalena")
         + p("Después vinieron la bahía de Samborombón, Punta Médanos y un primer susto: se cortaron los guardines. Se repararon a bordo y el piloto automático siguió andando. El 5 de enero, con las primeras luces, el velero entró a Mar del Plata."),
         media=["mar/salida a camaorones to Malvinas.jpg"]),
    dict(slug="mar-del-plata-y-puerto-belgrano", title="Mar del Plata y Puerto Belgrano", start=date(2024, 1, 5), end=date(2024, 1, 11),
         lead="Una escala en el Centro Naval y un chubasco que obligó a esperar a palo seco.",
         body=p("En Mar del Plata el Cabo de Hornos amarró en el Centro Naval. La meteorología marcaba un frente para el martes, así que la decisión fue seguir hasta Puerto Belgrano, dejarlo pasar y recién después bajar hacia Camarones.",
                "Zarpó la noche del 6 de enero. En la travesía apareció una línea de inestabilidad: 27 nudos de proa que se vieron venir de lejos y se esperaron a palo seco. Frente a Reta, ya con la guardia de la madrugada, el viento volvió a lo previsto.")
         + q("Si. Tuvimos un cubasxo con una línea de inestabilidad que nos puso 27 nudos de Jeta. Ahora está de acuerdo a lo previsto. Tomando la guardia ahora.", "8 de enero, frente a Reta")
         + p("El sudoeste del último tramo obligó a trincar mejor el ancla, que golpeaba con la ola. El velero entró a la Base Naval Puerto Belgrano a la nochecita del 8 y zarpó el 11 con rumbo sur.")),
    dict(slug="bahia-cracker", title="Los golfos y Bahía Cracker", start=date(2024, 1, 11), end=date(2024, 1, 15),
         lead="Ciento cuarenta y cinco millas en un día y un fondeadero que aguantó 30 nudos sin chistar.",
         body=p("Con viento norte de 20 a 25 nudos y genoa sola, el Cabo de Hornos hizo 145 millas en 24 horas. El pronóstico anunciaba un sudoeste de más de 30 nudos para el domingo 14, y con los amigos que seguían la meteorología desde tierra se decidió esperarlo en Bahía Cracker, en el golfo Nuevo.",
                "El 13 de enero fondearon detrás de unos cerros amesetados de 400 a 500 metros, en 7 metros de agua y a 300 metros de la costa.")
         + q("El ancla agarró Perfecto. Medialuna en el gráfico del ploter. Aguantó hasta ahora 30 nudos sin chistar.", "14 de enero, Bahía Cracker")
         + p("Hubo asado a bordo con amigos de Madryn, estreno del gomón y un día de playa para descansar. El 15 levaron el fondeo rumbo al sur."),
         media=[]),
    dict(slug="camarones", title="Camarones, esperando la ventana", start=date(2024, 1, 15), end=date(2024, 1, 19),
         lead="Con alerta de vientos fuertes de Comodoro para abajo, el velero se guardó en Camarones.",
         body=p("La idea inicial era cruzar desde Puerto Deseado, pero la alerta por vientos del sudoeste de 40 nudos para el miércoles y el jueves cambió los planes. El 16 de enero el Cabo de Hornos entró a Camarones para reabastecerse y esperar.")
         + q("Hola fernando / Acá guardados en Camarones. / Lugar hermoso.", "17 de enero, Camarones")
         + p("Desde ahí se fue armando la decisión del cruce: una ventana de tres días, el archivo GRIB cargado en el plóter y la idea de entrar a Malvinas por el norte. El 19 de enero, por la tarde, soltaron amarras."),
         media=[]),
    dict(slug="el-cruce", title="El cruce a Malvinas", start=date(2024, 1, 19), end=date(2024, 1, 22),
         lead="Rumbo 142 hacia la isla Gran Jason, la más occidental del archipiélago.",
         body=q("Reporte desde el velero cabo de Hornos. Navegando con rumbo 142 hacia la isla Grand Jason al oeste de la Gran Malvina. Viento del 070 de 12 nudos. Con vela Mayor R1 y genoa 1. Velocidad 6 nds. Distancia al WP: 251 MN. Tripulación y embarcación sin novedad. Saludos a la AsoProm 90.", "20 de enero")
         + p("El pronóstico se fue cumpliendo «fielmente». El 21, con 20 nudos del noroeste y 7 nudos de velocidad, la tripulación evaluó ser más agresiva con el rumbo y apuntar más al este. Esa noche quedaban 110 millas a la isla Gran Jason.",
             "Antes de llegar había que cumplir con los requisitos de entrada: avisar por correo 24 horas antes de cruzar la línea de reporte y comunicarse con Stanley Port Control por el canal 15.")
         + q("Malvinas (Islas Jason) a la vista!!! / Ahora rumbo 109 a Cape Dolphin. / 19 hs haremos ceremonia naval por el Aviso Sobral y Cap. Gomez Roca.", "22 de enero, 10 h"),
         media=["mar/malvinas1.jpg", "mar/garmin entrada a malvinas.jpg", "mar/nav norte malvinas delfines.mp4"]),
    dict(slug="el-homenaje", title="El homenaje al ARA «Alférez Sobral»", start=date(2024, 1, 22), end=date(2024, 1, 22),
         lead="Frente a la costa norte de las islas, el Cabo de Hornos rindió honores al aviso y a sus caídos.",
         body=p("Navegando hacia Cape Dolphin con 20 a 24 nudos del oeste, el velero llegó a la zona elegida al caer la tarde del 22 de enero. Allí se hizo la ceremonia que la Promoción 90 había pedido.")
         + q("Misión cumplida. Ceremonia realizada con los honores correspondientes. Más allá de la emoción propia que genera, fue increíble porque se acercaron un montón de toninas overas y delfines. Y cuando la corona estaba en el agua flotando por popa, dos toninas saltaron, una a cada lado.", "22 de enero, 19.30 h")
         + p('La historia completa del aviso, del pedido de la Promoción 90 y de la ceremonia está en la página <a href="../sobral.html">Homenaje al ARA «Alférez Sobral»</a>.'),
         media=["lagrimas/Sobral/IMG_3615.JPG", "mar/garmin ceremonia sobral.jpg"]),
    dict(slug="puerto-argentino", title="Puerto Argentino", start=date(2024, 1, 23), end=date(2024, 1, 26),
         lead="Más de 30 nudos para fondear, un amarre complicado y una visita al cementerio de Darwin.",
         body=p("El 23 de enero el Cabo de Hornos cruzó la línea de reporte entre la neblina. Stanley Port Control lo mandó a fondear y esperar instrucciones, con la bandera inglesa y la Q izadas. La bahía lo recibió con más de 30 nudos.")
         + q("Estamos amarrados con el barco al muelle. Lo atraque con más de 30 nudos de viento al lado de unos franceses. Una locura que gracias a dios no rompí nada", "23 de enero, Puerto Argentino")
         + p("La recepción fue «más que amable y cálida», aunque la conexión resultó casi imposible: sin wifi libre ni datos en los chips. El 24 la tripulación fue al cementerio de Darwin y a una pingüinera; el 25, a Tumbledown, donde combatió el BIM 5.")
         + q("Fui a Darwin. Me acorde de vos y recé por aquellos que están ahí.", "26 de enero"),
         media=["lagrimas/pozo de zorro malvinas.jpg", "lagrimas/Darwin/IMG_3599.MOV"]),
    dict(slug="garden-point", title="Garden Point: dos anclas y 120 metros de cadena", start=date(2024, 1, 26), end=date(2024, 1, 28),
         lead="Un nortazo en el fondeo y la decisión de no salir a buscar 45 nudos en el medio del mar.",
         body=p("El 26 zarparon de Puerto Argentino hacia el sudoeste y llegaron a Garden Point con lo último de luz. Esa madrugada el ancla garreó dos veces. Con 37 nudos se tiró la segunda ancla y los 120 metros de cadena, y recién ahí el velero quedó firme.",
                "El pronóstico anunciaba más de 45 nudos del norte para el 30 de enero, sin tiempo para llegar al continente. La discusión con los asesores en tierra fue franca.")
         + q("Que es lo que hace que tengamos que salir a enfrentar eso? El tiempo de espera no debe ser una variante a analizar... siempre las cosas cambian.", "27 de enero, Garden Point")
         + p("La decisión fue esperar y moverse dentro del archipiélago hacia el oeste para acortar el cruce de vuelta.")),
    dict(slug="la-vuelta-al-continente", title="La vuelta al continente", start=date(2024, 1, 28), end=date(2024, 1, 31),
         lead="De camino a New Island se abrió la ventana: rumbo directo a San Julián.",
         body=p("El 28 el Cabo de Hornos salió hacia New Island, la isla más occidental. Al amanecer del 29, con el pronóstico más atenuado y a 288 millas de San Julián, se decidió seguir derecho al continente.")
         + q("Genial. Todo ok. Picada, chori, colita a la parrilla, ensalada, papa al horno, vino, mantecol, truco, negro, siesta.", "29 de enero, en el cruce")
         + p("La noche del 30 el motor se paró: no llegaba gasoil. Se desarmó todo el circuito, se cambiaron los filtros y se purgó hasta encontrar la basura. El 31 de enero, con la pleamar, el velero entró a Puerto San Julián."),
         media=["arribo"]),
    dict(slug="san-julian", title="San Julián", start=date(2024, 1, 31), end=date(2024, 2, 8),
         lead="Cambio de tripulación y una semana de espera: «nunca se vio tanto norte».",
         body=p("En el Club Náutico El Delfín de San Julián hubo cambio de tripulación y, por fin, conexión telefónica. El viento del norte no daba tregua para cruzar el golfo San Jorge.")
         + q("Acá en San Julian esperando una ventana medianamente tranquila para cruzar el San Jorge... nunca se vio tanto Norte", "4 de febrero"),
         media=[]),
    dict(slug="caleta-hornos", title="El golfo San Jorge y Caleta Hornos", start=date(2024, 2, 8), end=date(2024, 2, 12),
         lead="Piloto automático roto, un perno improvisado y dos cabos a tierra en Caleta Hornos.",
         body=p("El cruce del golfo San Jorge empezó con el piloto automático fuera de servicio y horas de timón a mano. Ya arreglado, la noche siguiente se partió el bulón que une el brazo del piloto con la caña del sector. Había a bordo con qué improvisar.",
                "El 10 de febrero el velero se refugió en Caleta Hornos para dejar pasar un sudoeste de 40 nudos: fondeo y dos cabos a tierra, sin olas, tapados por los cerros.")
         + q("El anemómetro llegó a 38 nudos... bien guardados!!", "12 de febrero, Caleta Hornos")
         + p("La espera tuvo su premio: róbalos, pez gallo, mejillones y almejas de la pesca del día. El 12 por la tarde zarparon frente a Camarones."),
         media=[]),
    dict(slug="peninsula-valdes", title="Península Valdés", start=date(2024, 2, 12), end=date(2024, 2, 17),
         lead="Ola, viento de proa y una caja que perdía aceite: «esto se está pareciendo a Odiseo».",
         body=p("La subida hacia Valdés fue lenta, con viento y ola de proa. El perno del piloto se rompió dos veces más y la caja empezó a perder aceite por el eje. Puerto Pirámides sirvió para cargar agua, víveres y gasoil, y para esperar un sudsudoeste de 50 nudos.")
         + q("Esto se está pareciendo a Odiseo y su viaje", "14 de febrero")
         + p("El 17 salieron del golfo. La caja perdió 300 mililitros, que se recuperaron y midieron con jeringa."),
         media=[]),
    dict(slug="el-regreso", title="El regreso a casa", start=date(2024, 2, 17), end=date(2024, 2, 24),
         lead="Puerto Belgrano, Necochea a la vista y la llegada a Núñez.",
         body=p("Con mayor, genoa y apoyo del motor, el Cabo de Hornos subió con días agradables y noches de luna. El 19 de febrero entró por las boyas de la Base Naval Puerto Belgrano y el 21 retomó la navegación.")
         + q("Recibido juan. Vamos muy bien. El chubasco que me dijiste era el que había pasado. Fue una noche muy agradable a buen ritmo", "23 de febrero")
         + p("El 24 de febrero, a tres horas de Núñez, esperaban en el muelle la familia y los compañeros de promoción del padre de Francho."),
         media=["arribo", "gracias"]),
]


def rel(depth):
    return "../" * depth


def header(depth, current):
    nav = "".join(
        f'<a href="{rel(depth)}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for label, href in NAV)
    return (f'<a class="skip-link" href="#contenido">Saltar al contenido</a>\n'
            f'<header class="site-header"><div class="shell header-inner"><a class="brand" href="{rel(depth)}index.html" aria-label="{SITE}, inicio">'
            f'<span class="brand-mark" aria-hidden="true">CdH</span><span>{SITE}</span></a>'
            f'<nav class="nav" aria-label="Navegación principal">{nav}</nav></div></header>')


def footer(depth):
    return (f'<footer class="site-footer"><div class="shell footer-inner"><div><strong>{SITE}</strong>'
            f'<p>Velero Cabo de Hornos · enero y febrero de 2024.</p></div><div class="footer-links">'
            f'<a href="{rel(depth)}pages/bitacora/index.html">Bitácora</a><a href="{rel(depth)}pages/sobral.html">Homenaje</a>'
            f'<a href="https://www.instagram.com/ricardofranzosi/" target="_blank" rel="noopener noreferrer">Instagram</a></div></div></footer>')


def page(depth, current, title, description, main, extra_head="", scripts=""):
    css = f'<link rel="stylesheet" href="{rel(depth)}css/styles.css"><link rel="stylesheet" href="{rel(depth)}css/bitacora.css">'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#0b3440">
<title>{html.escape(title)}</title>
{css}
<link rel="icon" type="image/svg+xml" href="{rel(depth)}assets/favicon.svg">
{extra_head}
</head>
<body>
{header(depth, current)}
{main}
{footer(depth)}
{scripts}
</body>
</html>
"""


def draft(text):
    return f'<p class="draft-note"><strong>Borrador:</strong> {text}</p>' if DRAFT else ""


def media_block(name, depth):
    """Muestra el archivo si ya está en assets; si no, un recuadro pendiente."""
    stem = Path(name).stem
    for folder, kind in (("assets/videos", "video"), ("assets/images", "img")):
        for f in (ROOT / folder).glob(f"{slug(stem)}.*") if (ROOT / folder).exists() else []:
            src = f"{rel(depth)}{folder}/{f.name}"
            if kind == "video":
                return f'<figure class="video-card"><video controls preload="metadata" src="{src}"></video></figure>'
            return f'<figure class="post-photo"><img src="{src}" alt="" loading="lazy"></figure>'
    return f'<div class="media-pending"><strong>Foto o video pendiente</strong><span>AGUA SALADA / {html.escape(name)}</span></div>'


def slug(text):
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def fecha(d1, d2=None):
    if not d2 or d1 == d2:
        return f"{d1.day} de {MESES[d1.month - 1]} de {d1.year}"
    if d1.month == d2.month:
        return f"{d1.day} al {d2.day} de {MESES[d1.month - 1]} de {d1.year}"
    return f"{d1.day} de {MESES[d1.month - 1]} al {d2.day} de {MESES[d2.month - 1]} de {d2.year}"


def miles(n):
    return f"{n:,.0f}".replace(",", ".")


def load_track():
    text = (ROOT / "data" / "track.js").read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rstrip().rstrip(";").rindex("}") + 1])


def chapter_nm(track, ch):
    return sum(d["nm"] for d in track["days"]
               if ch["start"].isoformat() <= d["date"] < ch["end"].isoformat()
               or (ch["start"] == ch["end"] and d["date"] == ch["start"].isoformat()))


def build_chapters(track):
    total = len(CHAPTERS)
    for i, ch in enumerate(CHAPTERS):
        stage = next(s for s in STAGES if s[2] <= i < s[3])
        nm_ch = chapter_nm(track, ch)
        meta = f'<div class="logbook-meta"><span>{stage[0]}</span><span>{fecha(ch["start"], ch["end"])}</span>'
        if nm_ch >= 1:
            meta += f"<span>{miles(nm_ch)} millas náuticas</span>"
        meta += "</div>"
        media = "".join(media_block(m, 2) for m in ch.get("media", []))
        prev_link = (f'<a href="./{CHAPTERS[i - 1]["slug"]}.html"><span>Anterior</span><strong>{CHAPTERS[i - 1]["title"]}</strong></a>'
                     if i else '<a href="./index.html"><span>Bitácora</span><strong>Volver al índice</strong></a>')
        next_link = (f'<a href="./{CHAPTERS[i + 1]["slug"]}.html"><span>Siguiente</span><strong>{CHAPTERS[i + 1]["title"]}</strong></a>'
                     if i + 1 < total else '<a href="../sobral.html"><span>Para cerrar</span><strong>Homenaje al ARA «Alférez Sobral»</strong></a>')
        main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero">'
                f'<p class="eyebrow">Capítulo {i + 1} de {total} · {stage[0]}</p><h1>{ch["title"]}</h1>'
                f'<p class="lead">{ch["lead"]}</p>{meta}</section>'
                f'<article class="journal-entry card"><div class="journal-entry-body">'
                f'{draft("texto armado a partir de los mensajes del inReach; corregir y ampliar a gusto.")}'
                f'{ch["body"]}{media}</div></article>'
                f'<nav class="chapter-nav" aria-label="Capítulos">{prev_link}{next_link}</nav></main>')
        out = ROOT / "pages" / "bitacora" / f'{ch["slug"]}.html'
        out.write_text(page(2, "pages/bitacora/index.html", f'{ch["title"]} · {SITE}', ch["lead"], main), encoding="utf-8")


def build_bitacora_index(track):
    stages = ""
    for name, desc, a, b in STAGES:
        cards = ""
        for ch in CHAPTERS[a:b]:
            cards += (f'<article class="timeline-card"><p class="timeline-date">{fecha(ch["start"], ch["end"]).upper()}</p>'
                      f'<h3>{ch["title"]}</h3><p>{ch["lead"]}</p><a href="./{ch["slug"]}.html">Leer capítulo →</a></article>')
        stages += (f'<section class="timeline-stage"><header><div><p class="eyebrow">Etapa</p><h2>{name}</h2></div>'
                   f'<p>{desc}</p></header><div class="timeline-grid">{cards}</div></section>')
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">Bitácora</p>'
            f'<h1>Cincuenta y cinco días de agua salada</h1><p class="lead">El viaje contado en {len(CHAPTERS)} capítulos, desde la zarpada en Núñez hasta el regreso, '
            f'con las palabras que salieron del inReach mientras se navegaba.</p></section>{stages}</main>')
    (ROOT / "pages" / "bitacora" / "index.html").write_text(
        page(2, "pages/bitacora/index.html", f"Bitácora · {SITE}", "Bitácora de la travesía del velero Cabo de Hornos a Malvinas.", main), encoding="utf-8")


def stats(track):
    s = track["summary"]
    return (f'<div class="stats-row"><div class="stat"><strong>{miles(s["totalNm"])}</strong><span>millas náuticas navegadas</span></div>'
            f'<div class="stat"><strong>{s["days"]}</strong><span>días de travesía</span></div>'
            f'<div class="stat"><strong>{f"{abs(s['southmost']):.1f}".replace(".", ",")}°S</strong><span>latitud más austral</span></div>'
            f'<div class="stat"><strong>22/1</strong><span>homenaje al ARA «Alférez Sobral»</span></div></div>')


def build_index(track):
    phases = "".join(f'<tr><th scope="row">{ph["name"]}</th><td>{miles(ph["nm"])} MN</td></tr>' for ph in track["summary"]["phases"])
    journey = ""
    for n, (name, desc, a, _) in enumerate(STAGES, 1):
        journey += (f'<a class="journey-card" href="./pages/bitacora/{CHAPTERS[a]["slug"]}.html"><span>0{n}</span>'
                    f'<strong>{name}</strong><small>{desc}</small></a>')
    journey += ('<a class="journey-card journey-card-featured" href="./pages/sobral.html"><span>22 · 01 · 2024</span>'
                '<strong>Homenaje al ARA «Alférez Sobral»</strong><small>La ceremonia naval frente a las islas, a pedido de la Promoción 90.</small></a>')
    main = f"""<main id="contenido">
<section class="hero"><div class="shell hero-grid"><div class="hero-copy">
<p class="eyebrow">Velero Cabo de Hornos · enero y febrero de 2024</p>
<h1>Agua salada: rumbo a Malvinas</h1>
<p class="lead">Una travesía desde Buenos Aires hasta las islas para rendir homenaje al aviso ARA «Alférez Sobral» y a sus caídos, y volver navegando la costa patagónica.</p>
<div class="hero-actions"><a class="button" href="./pages/bitacora/index.html">Leer la bitácora</a><a class="text-link" href="./pages/sobral.html">El homenaje <span aria-hidden="true">→</span></a><a class="text-link" href="./cartografia.html">El recorrido <span aria-hidden="true">→</span></a></div>
{stats(track)}
</div>
<figure class="hero-media">{media_block("mar/malvinas1.jpg", 0)}<figcaption>Malvinas a la vista · 22 de enero de 2024</figcaption></figure>
</div></section>
<section class="shell"><div class="memorial"><p class="eyebrow">Homenaje · 22 de enero de 2024</p><h2>«Misión cumplida»</h2>
<p>Frente a la costa norte de las islas, la tripulación del Cabo de Hornos rindió honores al aviso ARA «Alférez Sobral», a su comandante, el capitán de corbeta Sergio Gómez Roca, y a los hombres que cayeron con él en mayo de 1982. Cuando la corona flotaba por la popa, dos toninas overas saltaron, una a cada lado.</p>
<p><a class="button" style="background:#fff;color:var(--navy)" href="./pages/sobral.html">Conocer la historia y ver la ceremonia</a></p></div></section>
<section class="journey-overview shell" aria-labelledby="ruta-viaje"><div class="journey-heading"><div><p class="eyebrow">Un viaje, tres etapas</p><h2 id="ruta-viaje">De Núñez a Malvinas y de vuelta</h2></div>
<p>La bitácora sigue el viaje en orden: la bajada por la costa, las islas y el regreso.</p></div><div class="journey-cards">{journey}</div></section>
<section class="shell"><article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Sobre la carta</p><h2>El recorrido completo</h2></header>
<p>El inReach del velero registró la posición durante toda la travesía. La cartografía permite seguirla día por día.</p>
<table class="nm-table"><tbody>{phases}<tr><th scope="row">Total</th><td>{miles(track["summary"]["totalNm"])} MN</td></tr></tbody></table>
<a class="gallery-link" href="./cartografia.html">Abrir la cartografía interactiva →</a></article></section>
<section class="shell video-section"><div class="section-heading video-heading"><div><p class="eyebrow">Videos</p><h2>Navegando al norte de Malvinas</h2></div><p>Delfines y toninas acompañando al Cabo de Hornos.</p></div>
{media_block("mar/nav norte malvinas delfines.mp4", 0)}<a class="gallery-link" href="./pages/videos.html">Ver todos los videos →</a></section>
</main>"""
    (ROOT / "index.html").write_text(
        page(0, "index.html", f"{SITE} · Velero Cabo de Hornos", "Travesía del velero Cabo de Hornos a Malvinas en 2024 y homenaje al ARA Alférez Sobral.", main,
             extra_head="<style>.nm-table{width:100%;max-width:520px;margin-top:1.2rem;border-collapse:collapse}.nm-table th,.nm-table td{padding:.5rem .7rem;border-bottom:1px solid var(--line);text-align:left}.nm-table td{text-align:right;color:var(--navy);font-weight:800}.nm-table tr:last-child th,.nm-table tr:last-child td{font-weight:800;border-bottom:0}</style>"),
        encoding="utf-8")


def build_sobral(track):
    leaflet = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">'
               '<style>#mapa-sobral{height:380px;border-radius:18px;margin-top:1.4rem;background:#dce9e8}.leaflet-container img{max-width:none!important}</style>')
    marker = next(m for m in track["markers"] if "Sobral" in m["name"])
    scripts = ('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script><script src="../data/track.js"></script><script>'
               "const m=L.map('mapa-sobral',{scrollWheelZoom:false});L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:12,attribution:'&copy; OpenStreetMap'}).addTo(m);"
               "const d=TRACK.days.filter(x=>x.date>='2024-01-20'&&x.date<='2024-01-23');d.forEach(x=>L.polyline(x.points,{color:'#1d7181',weight:4}).addTo(m));"
               f"L.circleMarker([{marker['lat']},{marker['lon']}],{{radius:9,color:'#fff',weight:3,fillColor:'#9a6840',fillOpacity:1}}).addTo(m).bindTooltip('Ceremonia · 22 de enero de 2024',{{permanent:true,direction:'top'}});"
               f"m.setView([{marker['lat']},{marker['lon']}],7);</script>")
    main = f"""<main class="shell" id="contenido">
<section class="page-hero chapter-hero"><p class="eyebrow">Homenaje · Promoción 90</p><h1>Homenaje al ARA «Alférez Sobral»</h1>
<p class="lead">El 22 de enero de 2024, frente a la costa norte de Malvinas, el velero Cabo de Hornos rindió honores al aviso, a su comandante y a sus caídos.</p></section>
{draft("revisar los datos históricos (marcados con ⚑ en el código) y completar los nombres de los caídos.")}
<section class="memorial"><p class="eyebrow">22 de enero de 2024 · 19.30 h</p><h2>La ceremonia en el mar</h2>
<p>El velero navegaba hacia Cape Dolphin con 20 a 24 nudos del oeste. Al llegar a la posición elegida, la tripulación formó en cubierta, se rindieron los honores correspondientes y se arrojó una corona al mar.</p>
<p>Mientras tanto, un grupo de toninas overas y delfines se acercó al barco. Cuando la corona flotaba por la popa, dos toninas saltaron, una a cada lado.</p>
<p>Esa misma noche salió el mensaje por el inReach: «Ceremonia de rendición de honores a los caídos del aviso ARA Sobral, realizada. Cumpliendo los deseos de los compañeros de la promoción 90 de la ESNM».</p></section>
<section class="video-grid" aria-label="Videos de la ceremonia">
<figure class="video-card video-featured">{media_block("lagrimas/Sobral/Ceremonia Sobral Completa.mp4", 1)}<figcaption><strong>La ceremonia completa</strong><span>Honores al ARA «Alférez Sobral» y al capitán Gómez Roca.</span></figcaption></figure>
<figure class="video-card">{media_block("lagrimas/Sobral/20240122_191308.mp4", 1)}<figcaption><strong>19.13 h · llegando a la posición</strong><span>Grabación original del 22 de enero.</span></figcaption></figure>
<figure class="video-card">{media_block("lagrimas/Sobral/IMG_3615.JPG", 1)}<figcaption><strong>La corona</strong><span>Foto de la ceremonia.</span></figcaption></figure>
</section>
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">El aviso</p><h2>El ARA «Alférez Sobral»</h2></header>
<p>El aviso ARA «Alférez Sobral» (A-9) era un remolcador de flota construido en los Estados Unidos durante la Segunda Guerra Mundial e incorporado a la Armada Argentina en 1972.<!-- ⚑ verificar: ex USS Salish (ATA-187) --> Llevaba el nombre del alférez José María Sobral, el primer argentino que invernó en la Antártida con la expedición sueca de Otto Nordenskjöld, entre 1901 y 1903.</p>
<p>En la noche del 2 al 3 de mayo de 1982, mientras buscaba a la tripulación de un bombardero Canberra derribado, el aviso fue atacado por helicópteros británicos con misiles. Uno impactó en el puente.<!-- ⚑ verificar hora y detalle del ataque --> Murieron su comandante, el capitán de corbeta Sergio Gómez Roca, y siete tripulantes. Con el puente destruido, el buque llegó por sus propios medios a Puerto Deseado.<!-- ⚑ verificar fecha de arribo: 5 de mayo --></p>
<div class="mini-note">⚑ Datos históricos para confirmar antes de publicar.</div></article>
<section class="memorial"><p class="eyebrow">Los caídos</p><h2>Honor y gloria</h2>
<ul class="fallen-list"><li>Capitán de corbeta Sergio Gómez Roca<small>Comandante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li><li>(nombre a completar)<small>Tripulante</small></li></ul></section>
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">El pedido</p><h2>La Promoción 90 y el otro Cabo de Hornos</h2></header>
<p>La ceremonia fue un pedido de los compañeros de la Promoción 90 de la ESNM, que quisieron que alguien llegara hasta esas aguas para rendir honores a su compañero caído.</p>
<p>La historia tenía además un hilo familiar. Desde el mar, Francho lo escribió así:</p>
{q("Alguna vez papá contó que estaba navegando cerca y quiso ir a auxiliar al Sobral con el \"Cabo de Hornos\" y no lo dejaron... Creo que si vio esto desde arriba estará contento que el \"Cabo de Hornos\" pudo ir a ver así compañero. Gracias por permitirnos ser parte de vuestro homenaje a su compañero. Será un honor que atesoraremos en nuestro corazón toda la vida!", "22 de enero de 2024")}
<p>Al regreso, el 24 de febrero, en el muelle de Núñez esperaban la familia y los compañeros de promoción de su padre.</p></article>
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Dónde</p><h2>La posición de la ceremonia</h2></header>
<p>Al norte del archipiélago, en la derrota hacia Cape Dolphin. La línea muestra el recorrido del velero entre el 20 y el 23 de enero.</p><div id="mapa-sobral" role="region" aria-label="Mapa de la posición de la ceremonia"></div></article>
</main>"""
    (ROOT / "pages" / "sobral.html").write_text(
        page(1, "pages/sobral.html", f"Homenaje al ARA Alférez Sobral · {SITE}",
             "Ceremonia naval del velero Cabo de Hornos en homenaje al aviso ARA Alférez Sobral y al capitán Gómez Roca, enero de 2024.",
             main, extra_head=leaflet, scripts=scripts), encoding="utf-8")


def build_simple_pages():
    videos = ["lagrimas/Sobral/Ceremonia Sobral Completa.mp4", "lagrimas/Sobral/20240122_191308.mp4",
              "mar/nav norte malvinas delfines.mp4", "mar/nav norte malvinas delfines 1.mp4",
              "mar/nav norte malvinas delfines 2.mp4", "lagrimas/Darwin/IMG_3599.MOV"]
    cards = "".join(f'<figure class="video-card{" video-featured" if i == 0 else ""}">{media_block(v, 1)}'
                    f'<figcaption><strong>{html.escape(Path(v).stem)}</strong><span>{html.escape(v)}</span></figcaption></figure>'
                    for i, v in enumerate(videos))
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">Videos</p><h1>El viaje en movimiento</h1>'
            f'<p class="lead">La ceremonia del Sobral, los delfines al norte de las islas y el resto de lo filmado a bordo.</p></section>'
            f'{draft("se completa con los 60 videos de AGUA SALADA y los reels de Instagram.")}<section class="video-grid">{cards}</section></main>')
    (ROOT / "pages" / "videos.html").write_text(page(1, "pages/videos.html", f"Videos · {SITE}", "Videos de la travesía del velero Cabo de Hornos a Malvinas.", main), encoding="utf-8")
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">Galería</p><h1>Fotos de la travesía</h1>'
            f'<p class="lead">Antecedentes, la navegación, Malvinas y el regreso.</p></section>'
            f'{draft("se arma con las carpetas antecedentes, sudor, mar, lágrimas, arribo y gracias.")}</main>')
    (ROOT / "pages" / "gallery.html").write_text(page(1, "pages/gallery.html", f"Galería · {SITE}", "Galería de fotos de la travesía del velero Cabo de Hornos.", main), encoding="utf-8")
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">El velero</p><h1>Cabo de Hornos</h1>'
            f'<p class="lead">El barco, su historia y la tripulación.</p></section>'
            f'{draft("completar con la ficha del velero (eslora, construcción, motor Perkins, equipamiento) y la tripulación.")}</main>')
    (ROOT / "pages" / "velero.html").write_text(page(1, "pages/velero.html", f"El velero · {SITE}", "El velero Cabo de Hornos y su tripulación.", main), encoding="utf-8")


CARTO_JS = r"""
const map=L.map('map',{scrollWheelZoom:false});
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:12,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const palette={ida:'#237887',malvinas:'#7256a5',regreso:'#c47743'};const names={ida:'rumbo al sur',malvinas:'Malvinas',regreso:'regreso'};
const status=document.getElementById('map-status');const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>new Intl.DateTimeFormat('es-AR',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(v+'T12:00:00Z'));
const data=window.TRACK;let dayIndex=data.days.length-1,layerMode='full',mapLayer=L.featureGroup(),currentMarker,playing=false,playTimer;
const draw=(fit=true)=>{map.removeLayer(mapLayer);mapLayer=L.featureGroup().addTo(map);const visible=data.days.slice(0,dayIndex+1).filter(d=>layerMode==='full'||d.phase===layerMode);let count=0,nm=0;
visible.forEach(d=>{if(d.points.length>1)L.polyline(d.points,{color:palette[d.phase],weight:4,opacity:.9,lineJoin:'round'}).addTo(mapLayer);count+=d.count;nm+=d.nm;});
const sel=data.days[dayIndex];const last=[...data.days.slice(0,dayIndex+1)].reverse().find(d=>d.points.length);
if(currentMarker)map.removeLayer(currentMarker);if(last){const pt=last.points.at(-1);currentMarker=L.circleMarker(pt,{radius:7,color:'#fff',weight:2,fillColor:palette[sel.phase],fillOpacity:1}).addTo(map).bindTooltip('Posición del '+sel.label,{direction:'top'});}
status.textContent=`${Math.round(nm).toLocaleString('es-AR')} MN hasta el ${sel.label}`;if(fit&&mapLayer.getLayers().length)map.fitBounds(mapLayer.getBounds(),{padding:[24,24],maxZoom:8});
document.querySelectorAll('[data-layer]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.layer===layerMode?'true':'false'));
document.getElementById('day-label').textContent=sel.label;document.getElementById('day-count').textContent=(sel.nm?`${sel.nm.toLocaleString('es-AR')} MN ese día · `:'En puerto o fondeado · ')+names[sel.phase];
document.getElementById('day-range').value=dayIndex;document.querySelectorAll('.day-button').forEach((b,i)=>b.setAttribute('aria-current',i===dayIndex?'true':'false'));};
const list=document.getElementById('day-list');data.days.forEach((d,i)=>{const b=document.createElement('button');b.type='button';b.className='day-button';b.innerHTML=`<strong>${esc(d.label)}</strong><span>${d.nm?d.nm.toLocaleString('es-AR')+' MN':'en puerto'}</span><em>${names[d.phase]}</em>`;b.addEventListener('click',()=>{dayIndex=i;draw();});list.appendChild(b);});
data.markers.forEach(mk=>{L.circleMarker([mk.lat,mk.lon],{radius:mk.name.includes('Sobral')?9:6,color:'#fff',weight:2,fillColor:mk.name.includes('Sobral')?'#9a6840':'#0b3440',fillOpacity:1}).addTo(map).bindTooltip(mk.name,{direction:'top',offset:[0,-6]});
const c=document.createElement('article');c.className='stop-card';c.innerHTML=`<strong>${esc(mk.name)}</strong><span>${esc(fmt(mk.date))}</span>`;document.getElementById('stop-list').appendChild(c);});
document.querySelectorAll('[data-layer]').forEach(b=>b.addEventListener('click',()=>{layerMode=b.dataset.layer;draw();}));
const range=document.getElementById('day-range');range.max=data.days.length-1;range.addEventListener('input',e=>{dayIndex=+e.target.value;draw(false);});
document.getElementById('play-button').addEventListener('click',()=>{const b=document.getElementById('play-button');if(playing){playing=false;clearInterval(playTimer);b.textContent='▶ Reproducir';return;}if(dayIndex>=data.days.length-1)dayIndex=0;playing=true;b.textContent='❚❚ Pausar';playTimer=setInterval(()=>{if(dayIndex>=data.days.length-1){playing=false;clearInterval(playTimer);b.textContent='▶ Reproducir';return;}dayIndex++;draw(false);},700);});
draw();
"""


def build_cartografia(track):
    s = track["summary"]
    rows = "".join(f'<tr><th scope="row">{ph["name"]}</th><td>{miles(ph["nm"])} MN</td></tr>' for ph in s["phases"])
    buttons = "".join(f'<button type="button" data-layer="{k}" aria-pressed="false">{n}</button>'
                      for k, n in (("ida", "Rumbo al sur"), ("malvinas", "Malvinas"), ("regreso", "Regreso")))
    main = f"""<main id="contenido">
<section class="shell page-hero map-intro"><p class="eyebrow">Cartografía · Garmin inReach</p><h1>El viaje, día por día</h1>
<p class="lead">La ruta sale de las posiciones que el inReach del Cabo de Hornos transmitió durante toda la travesía, ordenadas por fecha y depuradas de saltos imposibles del GPS. Los recorridos en tierra por las islas no se cuentan como navegación.</p>
<table class="nm-table"><tbody>{rows}<tr><th scope="row">Total</th><td>{miles(s["totalNm"])} MN</td></tr></tbody></table></section>
<section class="shell map-card" aria-labelledby="mapa-titulo"><div class="map-toolbar" aria-label="Capas de la cartografía"><button type="button" data-layer="full" aria-pressed="true">Travesía completa</button>{buttons}<span class="map-status" id="map-status" role="status">Cargando track…</span></div>
<div id="map" role="region" aria-labelledby="mapa-titulo"></div><div class="map-caption"><p id="mapa-titulo"><strong>Cartografía interactiva:</strong> elegí una etapa o mové la línea de tiempo. El punto marrón es el lugar del homenaje al ARA «Alférez Sobral».</p>
<div class="route-key"><span class="key-item"><i class="key-line"></i> rumbo al sur</span><span class="key-item"><i class="key-line malvinas"></i> Malvinas</span><span class="key-item"><i class="key-line regreso"></i> regreso</span></div></div></section>
<section class="shell timeline-card" aria-labelledby="cronologia-titulo"><div class="timeline-heading"><div><p class="eyebrow">Lectura interactiva</p><h2 id="cronologia-titulo">Avance de la travesía</h2></div><p>Mové el control o elegí un día. El mapa muestra el recorrido acumulado hasta esa fecha.</p></div>
<div class="timeline-controls"><button class="control-button" type="button" id="play-button">▶ Reproducir</button><input id="day-range" type="range" min="0" max="0" value="0" step="1" aria-label="Día de la travesía"><div><div class="day-label" id="day-label">—</div><div class="day-count" id="day-count">—</div></div></div>
<div class="day-list" id="day-list" aria-label="Días de la travesía"></div></section>
<section class="shell" aria-labelledby="escala-titulo"><div class="section-heading"><div><p class="eyebrow">Escalas</p><h2 id="escala-titulo">Puertos y fondeaderos</h2></div></div><div class="stop-list" id="stop-list"></div></section>
</main>"""
    head = ('<link rel="stylesheet" href="./css/cartografia.css"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">'
            '<style>.nm-table{width:100%;max-width:520px;margin-top:1.2rem;border-collapse:collapse}.nm-table th,.nm-table td{padding:.5rem .7rem;border-bottom:1px solid var(--line);text-align:left}.nm-table td{text-align:right;color:var(--navy);font-weight:800}.nm-table tr:last-child th,.nm-table tr:last-child td{font-weight:800;border-bottom:0}.timeline-card{display:grid}</style>')
    scripts = f'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script><script src="./data/track.js"></script><script>{CARTO_JS}</script>'
    (ROOT / "cartografia.html").write_text(
        page(0, "cartografia.html", f"Cartografía · {SITE}", "Recorrido día por día del velero Cabo de Hornos en su travesía a Malvinas.", main, head, scripts), encoding="utf-8")


def main():
    track = load_track()
    build_cartografia(track)
    build_chapters(track)
    build_bitacora_index(track)
    build_index(track)
    build_sobral(track)
    build_simple_pages()
    print(f"Sitio generado: {len(CHAPTERS)} capítulos · {miles(track['summary']['totalNm'])} MN")


if __name__ == "__main__":
    main()
