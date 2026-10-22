#!/usr/bin/env python3
"""Genera el sitio estático de la travesía del velero Cabo de Hornos a Malvinas.

Uso: python scripts/build_site.py

Sigue la estructura de la charla «Agua salada» (antecedentes, sudor, mar, lágrimas,
regreso y gracias). Lee data/track.js (de build_track.py) para las millas de cada
capítulo. Las fotos están en assets/images/charla y los videos en assets/videos;
un archivo que todavía no está se muestra como recuadro "pendiente".
"""
import html
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = True  # muestra avisos de borrador; pasar a False antes de publicar
SITE = "Agua salada"
SUBTITLE = "Velero Cabo de Hornos · travesía a Malvinas 2024"
ATLANTIS = "https://ricardo-franzosi.github.io/atlantis-fin-del-mundo/"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

NAV = [
    ("Inicio", "index.html"),
    ("Antecedentes", "pages/antecedentes.html"),
    ("El velero", "pages/velero.html"),
    ("Bitácora", "pages/bitacora/index.html"),
    ("Cartografía", "cartografia.html"),
    ("Homenaje al Sobral", "pages/sobral.html"),
    ("Videos", "pages/videos.html"),
    ("Galería", "pages/gallery.html"),
]

# Etapas de la bitácora: nombre, descripción y rango de capítulos [desde, hasta)
STAGES = [
    ("El mar", "Del Centro Naval Núñez a la costa patagónica, esperando la ventana para cruzar.", 0, 4),
    ("Malvinas", "El cruce, el homenaje al ARA «Alférez Sobral», Puerto Argentino, Tumbledown y Darwin.", 4, 8),
    ("Sudor II · El regreso a Ítaca", "Como Odiseo: Garden Point, San Julián, Caleta Hornos, Valdés y la vuelta a casa.", 8, 14),
]

# Videos convertidos para la web (H.264 720p): id -> (título, descripción)
VIDEOS = {
    "navegando-a-malvinas": ("Agua salada", "Navegando hacia las islas, la mañana del 22 de enero."),
    "preparativos": ("Sudor I", "Los preparativos del velero."),
    "zarpada": ("La zarpada", "Saliendo del Centro Naval Núñez."),
    "rumbo-a-puerto-belgrano": ("Rumbo a Puerto Belgrano", "Navegando el 7 de enero."),
    "el-cruce": ("El cruce", "Zarpando de Camarones hacia Malvinas, 19 de enero."),
    "ceremonia-sobral": ("Ceremonia naval en homenaje al ARA «Alférez Sobral»", "22 de enero de 2024, frente a la costa norte de las islas."),
    "tumbledown": ("Tumbledown", "25 de enero."),
    "darwin-1": ("Cementerio de Darwin", "24 de enero."),
    "darwin-2": ("Cementerio de Darwin", "24 de enero."),
    "darwin-3": ("Darwin", "Recorrido por el cementerio."),
    "regreso-1": ("El regreso", "Sudor II."),
    "regreso-2": ("El regreso", "Sudor II."),
}

# Fotos por sección: (archivo en assets/images/charla, epígrafe)
PHOTOS = {
    "intro": [("d02-image2", "")],
    "liceo": [("d03-image3", "Liceo Naval Militar «Almirante Guillermo Brown»"), ("d03-image4", "El banderín de la XXXV promoción, con las Malvinas como motivo"),
              ("d03-image5", "La XXXV"), ("d03-image7", ""), ("d03-image9", ""), ("d03-image8", ""), ("d03-image6", "")],
    "atlantis": [("d03-image10", "Con el Atlantis en la Antártida")],
    "transporte": [("d04-image14", "Transporte ARA B-5 «Cabo de Hornos»"), ("d04-image11", "El transporte en un sello postal"),
                   ("d04-image15", "Desembarco de los Super Étendard traídos desde Francia por el transporte ARA «Cabo de Hornos», al terminar la guerra"),
                   ("d04-image12", "El escudo del ARA «Cabo de Hornos»"), ("d04-image16", "")],
    "familia": [("d27-image134", ""), ("d27-image135", "")],
    "sudor1": [("d05-image18", "Así lo recibimos en 2017, con el casco azul"), ("d05-image17", ""), ("d05-image19", "El casco azul original"), ("d05-image22", "El casco, de nuevo rojo"),
               ("d05-image20", ""), ("d05-image21", ""), ("d05-image23", ""), ("d05-image24", "")],
    "sudor1b": [("d06-image25", ""), ("d06-image26", ""), ("d06-image27", ""), ("d06-image28", ""), ("d06-image29", ""),
                ("d06-image30", "El motor nuevo"), ("d06-image36", ""), ("d06-image34", ""), ("d06-image33", ""),
                ("d06-image35", ""), ("d06-image32", ""), ("d06-image31", ""), ("d06-image37", "")],
    "mar-del-plata-y-puerto-belgrano": [("d07-image39", "El Cabo de Hornos en Mar del Plata"), ("d08-image44", ""), ("d08-image45", ""), ("d08-image47", "Asado a bordo"),
                                        ("d08-image46", ""), ("d08-image48", ""), ("d08-image49", ""), ("d08-image50", "")],
    "bahia-cracker": [("d09-image51", "El Cabo de Hornos fondeado"), ("d09-image53", ""), ("d09-image54", ""),
                      ("d09-image55", ""), ("d09-image56", ""), ("d09-image57", ""), ("d09-image58", "")],
    "camarones": [("d10-image60", ""), ("d10-image59", ""), ("d10-image62", ""), ("d10-image67", ""), ("d10-image64", ""),
                  ("d10-image65", ""), ("d10-image61", ""), ("d10-image63", ""), ("d10-image66", "")],
    "el-cruce": [("d11-image71", "Puerto Argentino a la vista"), ("d11-image68", "")],
    "el-homenaje": [("d15-image82", "Ceremonia en honor al capitán Gómez Roca y sus hombres caídos en el ARA «Sobral»")],
    "puerto-argentino": [("d12-image75", ""), ("d12-image73", ""), ("d12-image74", ""), ("d12-image76", ""),
                         ("d13-image77", ""), ("d13-image78", ""), ("d13-image79", ""), ("d13-image80", "")],
    "tumbledown": [("d16-image86", ""), ("d16-image87", ""), ("d16-image88", ""), ("d16-image89", ""),
                   ("d17-image93", ""), ("d17-image95", ""), ("d17-image91", ""), ("d17-image90", ""), ("d17-image92", ""),
                   ("d17-image94", ""), ("d17-image96", ""), ("d18-image97", ""), ("d18-image98", ""), ("d18-image99", ""),
                   ("d18-image100", ""), ("d18-image101", "")],
    "darwin": [("d19-image102", "El cementerio de Darwin"), ("d19-image103", ""), ("d19-image104", "Soldado argentino solo conocido por Dios"),
               ("d20-image105", ""), ("d20-image106", "")],
    "garden-point": [("d21-image109", ""), ("d21-image107", ""), ("d21-image110", ""), ("d21-image111", "")],
    "san-julian": [("d22-image116", ""), ("d22-image114", ""), ("d22-image115", "")],
    "caleta-hornos": [("d23-image117", "Fondeados en Caleta Hornos"), ("d23-image118", ""), ("d23-image119", "Mejillones y almejas"),
                      ("d23-image120", ""), ("d23-image121", ""), ("d23-image122", ""), ("d23-image123", "")],
    "peninsula-valdes": [("d24-image125", ""), ("d24-image124", ""), ("d25-image126", ""), ("d25-image127", ""),
                         ("d25-image128", ""), ("d25-image129", ""), ("d25-image130", "")],
    "el-regreso": [("d26-image131", ""), ("d26-image133", ""), ("d26-image132", "")],
    "gracias": [("d28-image137", ""), ("d28-image139", ""), ("d28-image138", ""), ("d28-image140", ""), ("d28-image136", "")],
    "sobral": [("d15-image83", ""), ("d15-image85", "")],
}


def q(text, cite):
    """Cita textual de un mensaje del inReach."""
    return (f'<blockquote class="inreach-quote">{html.escape(text)}'
            f'<cite>Mensaje enviado por inReach · {html.escape(cite)}</cite></blockquote>')


def p(*paras):
    return "".join(f"<p>{x}</p>" for x in paras)


CHAPTERS = [
    dict(slug="la-zarpada", title="La zarpada y el Río de la Plata", start=date(2024, 1, 3), end=date(2024, 1, 5),
         lead="Del Centro Naval Núñez a Mar del Plata, con viento y ola de proa desde la primera noche.", videos=["zarpada"],
         body=p("El Cabo de Hornos zarpó del Centro Naval Núñez en la madrugada del 3 de enero de 2024, más tarde de lo previsto. La primera prueba del inReach salió frente a Punta Lara, con 16 nudos del ENE y bastante ola «de jeta»: a motor y sin velas.",
                "La primera noche ya mostró el carácter del río: 25 nudos del este, rizo tres y trinquetilla, tirando bordes para pasar Magdalena. Al amanecer del 4, virando Punta Piedras, la tripulación pudo relajarse un poco.")
         + q("Estamo con R3 y rinquetilla. Mucha ola para motor. Tirando bordes... acá 25 nudos del este. Pasando magdalena", "4 de enero, frente a Magdalena")
         + p("Después vinieron la bahía de Samborombón, Punta Médanos y un primer susto: se cortaron los guardines. Se repararon a bordo y el piloto automático siguió andando. El 5 de enero, con las primeras luces, el velero entró a Mar del Plata.")),
    dict(slug="mar-del-plata-y-puerto-belgrano", title="Mar del Plata y Puerto Belgrano", start=date(2024, 1, 5), end=date(2024, 1, 11),
         lead="Una escala en el Centro Naval y un chubasco que obligó a esperar a palo seco.", videos=["rumbo-a-puerto-belgrano"],
         body=p("En Mar del Plata el Cabo de Hornos amarró en el Centro Naval. La meteorología marcaba un frente para el martes, así que la decisión fue seguir hasta Puerto Belgrano, dejarlo pasar y recién después bajar hacia Camarones.",
                "Zarpó la noche del 6 de enero. En la travesía apareció una línea de inestabilidad: 27 nudos de proa que se vieron venir de lejos y se esperaron a palo seco. Frente a Reta, ya con la guardia de la madrugada, el viento volvió a lo previsto.")
         + q("Si. Tuvimos un cubasxo con una línea de inestabilidad que nos puso 27 nudos de Jeta. Ahora está de acuerdo a lo previsto. Tomando la guardia ahora.", "8 de enero, frente a Reta")
         + p("El sudoeste del último tramo obligó a trincar mejor el ancla, que golpeaba con la ola. El velero entró a la Base Naval Puerto Belgrano a la nochecita del 8 y zarpó el 11 con rumbo sur.")),
    dict(slug="bahia-cracker", title="Los golfos y Bahía Cracker", start=date(2024, 1, 11), end=date(2024, 1, 15),
         lead="Ciento cuarenta y cinco millas en un día y un fondeadero que aguantó 30 nudos sin chistar.",
         body=p("Con viento norte de 20 a 25 nudos y genoa sola, el Cabo de Hornos hizo 145 millas en 24 horas. El pronóstico anunciaba un sudoeste de más de 30 nudos para el domingo 14, y con los amigos que seguían la meteorología desde tierra se decidió esperarlo en Bahía Cracker, en el golfo Nuevo.",
                "El 13 de enero fondearon detrás de unos cerros amesetados de 400 a 500 metros, en 7 metros de agua y a 300 metros de la costa.")
         + q("El ancla agarró Perfecto. Medialuna en el gráfico del ploter. Aguantó hasta ahora 30 nudos sin chistar.", "14 de enero, Bahía Cracker")
         + p("Hubo asado a bordo con amigos de Madryn, estreno del gomón y un día de playa para descansar. El 15 levaron el fondeo rumbo al sur.")),
    dict(slug="camarones", title="Camarones, esperando la ventana", start=date(2024, 1, 15), end=date(2024, 1, 19),
         lead="Con alerta de vientos fuertes de Comodoro para abajo, el velero se guardó en Camarones.",
         body=p("La idea inicial era cruzar desde Puerto Deseado, pero la alerta por vientos del sudoeste de 40 nudos para el miércoles y el jueves cambió los planes. El 16 de enero el Cabo de Hornos entró a Camarones para reabastecerse y esperar.")
         + q("Hola fernando / Acá guardados en Camarones. / Lugar hermoso.", "17 de enero, Camarones")
         + p("Desde ahí se fue armando la decisión del cruce: una ventana de tres días, el archivo GRIB cargado en el plóter y la idea de entrar a Malvinas por el norte. El 19 de enero, por la tarde, soltaron amarras.")),
    dict(slug="el-cruce", title="El cruce a Malvinas", start=date(2024, 1, 19), end=date(2024, 1, 22),
         lead="Rumbo 142 hacia la isla Gran Jason, la más occidental del archipiélago.", videos=["el-cruce", "navegando-a-malvinas"],
         body=q("Reporte desde el velero cabo de Hornos. Navegando con rumbo 142 hacia la isla Grand Jason al oeste de la Gran Malvina. Viento del 070 de 12 nudos. Con vela Mayor R1 y genoa 1. Velocidad 6 nds. Distancia al WP: 251 MN. Tripulación y embarcación sin novedad. Saludos a la AsoProm 90.", "20 de enero")
         + p("El pronóstico se fue cumpliendo «fielmente». El 21, con 20 nudos del noroeste y 7 nudos de velocidad, la tripulación evaluó ser más agresiva con el rumbo y apuntar más al este. Esa noche quedaban 110 millas a la isla Gran Jason.",
             "Antes de llegar había que cumplir con los requisitos de entrada: avisar por correo 24 horas antes de cruzar la línea de reporte y comunicarse con Stanley Port Control por el canal 15.")
         + q("Malvinas (Islas Jason) a la vista!!! / Ahora rumbo 109 a Cape Dolphin. / 19 hs haremos ceremonia naval por el Aviso Sobral y Cap. Gomez Roca.", "22 de enero, 10 h")),
    dict(slug="el-homenaje", title="El homenaje al ARA «Alférez Sobral»", start=date(2024, 1, 22), end=date(2024, 1, 22),
         lead="Frente a la costa norte de las islas, el Cabo de Hornos rindió honores al aviso y a sus caídos.", videos=["ceremonia-sobral"],
         body=p("Navegando hacia Cape Dolphin con 20 a 24 nudos del oeste, el velero llegó a la zona elegida al caer la tarde del 22 de enero. Allí se hizo la ceremonia que la Promoción 90 de la ESNM había pedido.")
         + q("Misión cumplida. Ceremonia realizada con los honores correspondientes. Más allá de la emoción propia que genera, fue increíble porque se acercaron un montón de toninas overas y delfines. Y cuando la corona estaba en el agua flotando por popa, dos toninas saltaron, una a cada lado.", "22 de enero, 19.30 h")
         + p('La historia completa del aviso, del pedido de la Promoción 90 y de la ceremonia está en la página <a href="../sobral.html">Homenaje al ARA «Alférez Sobral»</a>.')),
    dict(slug="puerto-argentino", title="Puerto Argentino", start=date(2024, 1, 23), end=date(2024, 1, 24),
         lead="Más de 30 nudos para fondear, un amarre complicado y una recepción que no esperaban.",
         body=p("El 23 de enero el Cabo de Hornos cruzó la línea de reporte entre la neblina. Stanley Port Control lo mandó a fondear y esperar instrucciones, con la bandera inglesa y la Q izadas. La bahía lo recibió con más de 30 nudos.")
         + q("Estamos amarrados con el barco al muelle. Lo atraque con más de 30 nudos de viento al lado de unos franceses. Una locura que gracias a dios no rompí nada", "23 de enero, Puerto Argentino")
         + p("La recepción fue «más que amable y cálida», aunque la conexión resultó casi imposible: sin wifi libre ni datos en los chips.")),
    dict(slug="tumbledown-y-darwin", title="Lágrimas: Tumbledown y Darwin", start=date(2024, 1, 24), end=date(2024, 1, 26),
         lead="El cementerio de Darwin y el monte donde combatió el BIM 5. Gloria y honor a los muertos por la Patria.",
         videos=["darwin-1", "darwin-2", "darwin-3", "tumbledown"], extra_photos=["darwin"],
         body=p("El 24 de enero la tripulación fue al cementerio de Darwin. Entre los nombres grabados está el del capitán de corbeta Sergio Raúl Gómez Roca, comandante del ARA «Alférez Sobral», junto a las cruces de los soldados argentinos «solo conocidos por Dios».")
         + q("Fui a Darwin. Me acorde de vos y recé por aquellos que están ahí.", "26 de enero")
         + p("El 25 subieron a Tumbledown, donde combatió el Batallón de Infantería de Marina 5. En las piedras todavía quedan restos de aquellos días: vainas, latas y posiciones.")),
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
         + p("La noche del 30 el motor se paró: no llegaba gasoil. Se desarmó todo el circuito, se cambiaron los filtros y se purgó hasta encontrar la basura. El 31 de enero, con la pleamar, el velero entró a Puerto San Julián.")),
    dict(slug="san-julian", title="San Julián", start=date(2024, 1, 31), end=date(2024, 2, 7),
         lead="Cambio de tripulación y una semana de espera: «nunca se vio tanto norte».",
         body=p("En el Club Náutico El Delfín de San Julián hubo cambio de tripulación y, por fin, conexión telefónica. El viento del norte no daba tregua para cruzar el golfo San Jorge, y recién el 7 de febrero el Cabo de Hornos pudo zarpar.")
         + q("Acá en San Julian esperando una ventana medianamente tranquila para cruzar el San Jorge... nunca se vio tanto Norte", "4 de febrero")),
    dict(slug="caleta-hornos", title="El golfo San Jorge y Caleta Hornos", start=date(2024, 2, 7), end=date(2024, 2, 12),
         lead="Piloto automático roto, un perno improvisado y dos cabos a tierra en Caleta Hornos.", videos=["regreso-1"],
         body=p("El cruce del golfo San Jorge empezó con el piloto automático fuera de servicio y horas de timón a mano. Ya arreglado, la noche siguiente se partió el bulón que une el brazo del piloto con la caña del sector. Había a bordo con qué improvisar.",
                "El 10 de febrero el velero se refugió en Caleta Hornos para dejar pasar un sudoeste de 40 nudos: fondeo y dos cabos a tierra, sin olas, tapados por los cerros.")
         + q("El anemómetro llegó a 38 nudos... bien guardados!!", "12 de febrero, Caleta Hornos")
         + p("La espera tuvo su premio: róbalos, pez gallo, mejillones y almejas de la pesca del día. El 12 por la tarde zarparon frente a Camarones.")),
    dict(slug="peninsula-valdes", title="Península Valdés", start=date(2024, 2, 12), end=date(2024, 2, 17),
         lead="Ola, viento de proa y una caja que perdía aceite: «esto se está pareciendo a Odiseo».", videos=["regreso-2"],
         body=p("La subida hacia Valdés fue lenta, con viento y ola de proa. El perno del piloto se rompió dos veces más y la caja empezó a perder aceite por el eje. Puerto Pirámides sirvió para cargar agua, víveres y gasoil, y para esperar un sudsudoeste de 50 nudos.")
         + q("Esto se está pareciendo a Odiseo y su viaje", "14 de febrero")
         + p("El 17 salieron del golfo. La caja perdió 300 mililitros, que se recuperaron y midieron con jeringa.")),
    dict(slug="el-regreso", title="El regreso a casa", start=date(2024, 2, 17), end=date(2024, 2, 24),
         lead="Puerto Belgrano, Necochea a la vista y la llegada a Buenos Aires.",
         body=p("Con mayor, genoa y apoyo del motor, el Cabo de Hornos subió con días agradables y noches de luna. El 19 de febrero entró por las boyas de la Base Naval Puerto Belgrano y el 21 retomó la navegación.")
         + q("Recibido juan. Vamos muy bien. El chubasco que me dijiste era el que había pasado. Fue una noche muy agradable a buen ritmo", "23 de febrero")
         + p("El 24 de febrero, a tres horas de Núñez, esperaban en el muelle la familia y los compañeros de promoción de su padre.")),
]

THANKS = [
    ("Mar del Plata", "CN Daniel Corvalán, Ctre. Roberto Denis, TC Agustín Vázquez"),
    ("Base Naval Puerto Belgrano", "Cro. Rodrigo Ataun, CN Daniel Aldama, CN Guillermo Simoncini, C Alte. Gustavo Lio Pombo, Oscar Isa (ADAM y velero «Azul»), Omar Anziano, Andrea Gatica, Fernando Almada, Máximo Mónaco"),
    ("Camarones", "Mara y Ariel (Caleta Sara)"),
    ("San Julián", "Sergio Lasencion, Juan Pereira"),
    ("Malvinas", "LT Samanta Davis"),
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
            f'<p>{SUBTITLE}.</p></div><div class="footer-links">'
            f'<a href="{rel(depth)}pages/bitacora/index.html">Bitácora</a><a href="{rel(depth)}pages/sobral.html">Homenaje</a>'
            f'<a href="https://www.instagram.com/ricardofranzosi/" target="_blank" rel="noopener noreferrer">Instagram</a>'
            f'<a href="https://www.instagram.com/cdhsail/" target="_blank" rel="noopener noreferrer">@cdhsail</a></div></div></footer>')


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


def photo_src(name, depth):
    return f"{rel(depth)}assets/images/charla/{name}.jpg"


def photo(name, caption, depth, alt=""):
    if not (ROOT / "assets/images/charla" / f"{name}.jpg").exists():
        return f'<div class="media-pending"><strong>Foto pendiente</strong><span>{html.escape(name)}</span></div>'
    cap = f"<figcaption><span>{html.escape(caption)}</span></figcaption>" if caption else ""
    return (f'<figure class="photo-card"><a href="{photo_src(name, depth)}"><img src="{photo_src(name, depth)}" '
            f'alt="{html.escape(caption or alt)}" loading="lazy" decoding="async"></a>{cap}</figure>')


def photo_grid(key, depth, alt=""):
    items = PHOTOS.get(key, [])
    if not items:
        return ""
    return '<div class="gallery-grid gallery-dense">' + "".join(photo(n, c, depth, alt) for n, c in items) + "</div>"


def video(vid, depth, featured=False):
    title, desc = VIDEOS[vid]
    src = ROOT / "assets/videos" / f"{vid}.mp4"
    cls = "video-card video-featured" if featured else "video-card"
    if not src.exists():
        body = f'<div class="media-pending"><strong>Video en preparación</strong><span>{html.escape(vid)}.mp4</span></div>'
    else:
        poster = f' poster="{rel(depth)}assets/videos/{vid}.jpg"' if (ROOT / "assets/videos" / f"{vid}.jpg").exists() else ""
        body = f'<video controls preload="none"{poster} src="{rel(depth)}assets/videos/{vid}.mp4"></video>'
    return f'<figure class="{cls}">{body}<figcaption><strong>{html.escape(title)}</strong><span>{html.escape(desc)}</span></figcaption></figure>'


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
        if nm_ch >= 10:
            meta += f"<span>{miles(nm_ch)} millas náuticas</span>"
        meta += "</div>"
        vids = "".join(video(v, 2) for v in ch.get("videos", []))
        vids = f'<section class="video-grid" aria-label="Videos">{vids}</section>' if vids else ""
        photos = photo_grid(ch["slug"], 2, ch["title"]) + "".join(photo_grid(k, 2, ch["title"]) for k in ch.get("extra_photos", []))
        if ch["slug"] == "tumbledown-y-darwin":
            photos += "<h2 class='section-title'>Tumbledown</h2>" + photo_grid("tumbledown", 2, "Tumbledown")
        prev_link = (f'<a href="./{CHAPTERS[i - 1]["slug"]}.html"><span>Anterior</span><strong>{CHAPTERS[i - 1]["title"]}</strong></a>'
                     if i else '<a href="../velero.html"><span>Antes de zarpar</span><strong>Sudor I: el velero</strong></a>')
        next_link = (f'<a href="./{CHAPTERS[i + 1]["slug"]}.html"><span>Siguiente</span><strong>{CHAPTERS[i + 1]["title"]}</strong></a>'
                     if i + 1 < total else '<a href="../gracias.html"><span>Para cerrar</span><strong>Gracias</strong></a>')
        main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero">'
                f'<p class="eyebrow">Capítulo {i + 1} de {total} · {stage[0]}</p><h1>{ch["title"]}</h1>'
                f'<p class="lead">{ch["lead"]}</p>{meta}</section>'
                f'<article class="journal-entry card"><div class="journal-entry-body">'
                f'{draft("texto armado a partir de los mensajes del inReach; corregir y ampliar a gusto.")}'
                f'{ch["body"]}</div></article>{vids}{photos}'
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
            f'<h1>Cincuenta y tres días de agua salada</h1><p class="lead">El viaje contado en {len(CHAPTERS)} capítulos, del Centro Naval Núñez a Malvinas y de vuelta, '
            f'con las palabras que salieron del inReach mientras se navegaba.</p></section>{stages}</main>')
    (ROOT / "pages" / "bitacora" / "index.html").write_text(
        page(2, "pages/bitacora/index.html", f"Bitácora · {SITE}", "Bitácora de la travesía del velero Cabo de Hornos a Malvinas.", main), encoding="utf-8")


TIMELINE = [
    ("1979", "El transporte", "Entra en servicio el transporte ARA B-5 «Cabo de Hornos», de la clase Costa Sur.", "pages/antecedentes.html"),
    ("1982", "El Liceo Naval", "Ricardo ingresa al Liceo Naval Militar «Almirante Guillermo Brown» con la XXXV promoción. Su banderín lleva las Malvinas.", "pages/antecedentes.html"),
    ("Abril–junio de 1982", "La guerra", "Al mando del capitán de corbeta Ricardo Ángel Franzosi, el transporte «Cabo de Hornos» es buque logístico: lleva tropa y pertrechos.", "pages/antecedentes.html"),
    ("3 de mayo de 1982", "El «Sobral»", "Un misil destruye el puente del aviso ARA «Alférez Sobral». Mueren el capitán Gómez Roca y siete hombres. Desde el «Cabo de Hornos», su padre quiso ir en su auxilio y no lo dejaron.", "pages/sobral.html"),
    ("Fines de 1982", "Los Super Étendard", "Terminada la guerra, el transporte trae desde Francia los aviones Super Étendard de la Armada.", "pages/antecedentes.html"),
    ("2017", "La compra", "Llega el velero después de la compra, con el casco azul.", "pages/velero.html"),
    ("2017–2019", "La carroza", "En tierra, Jesús Vinacua le hace las modificaciones de la carroza.", "pages/velero.html"),
    ("2019–2024", "Sudor I", "Cinco años de preparación para su primera singladura.", "pages/velero.html"),
    ("2021–2022", "El Atlantis", "Mientras tanto, la expedición en velero de Buenos Aires a la Antártida.", "pages/antecedentes.html"),
    ("3 de enero de 2024", "La zarpada", "Primera singladura del velero «Cabo de Hornos»: zarpa del Centro Naval Núñez rumbo a Malvinas.", "pages/bitacora/la-zarpada.html"),
    ("22 de enero de 2024", "El homenaje", "Frente a la costa norte de las islas, ceremonia naval por el ARA «Alférez Sobral» y sus caídos.", "pages/sobral.html"),
    ("23 al 26 de enero de 2024", "Las islas", "Puerto Argentino, el cementerio de Darwin y Tumbledown.", "pages/bitacora/tumbledown-y-darwin.html"),
    ("24 de febrero de 2024", "El regreso a Ítaca", "Después de 3.465 millas náuticas, el velero vuelve a Buenos Aires.", "pages/bitacora/el-regreso.html"),
]


def timeline(depth):
    items = "".join(
        f'<li class="{"tl-1982" if y.endswith("1982") or y == "1982" else "tl-2024" if "2024" in y else ""}"><time>{html.escape(y)}</time>'
        f'<a href="{rel(depth)}{href}"><strong>{html.escape(t)}</strong><span>{html.escape(d)}</span></a></li>'
        for y, t, d, href in TIMELINE)
    return (f'<section class="shell timeline-1982" aria-labelledby="tl-titulo"><div class="journey-heading"><div><p class="eyebrow">Un mismo nombre, dos barcos</p>'
            f'<h2 id="tl-titulo">1982 → 2024</h2></div><p>El año de la guerra unió al Liceo Naval, al transporte «Cabo de Hornos» y al «Sobral». Cuarenta y dos años después, el velero cerró el círculo.</p></div>'
            f'<ol class="tl">{items}</ol></section>')


def stats(track):
    s = track["summary"]
    lat = f"{abs(s['southmost']):.1f}".replace(".", ",")
    return (f'<div class="stats-row"><div class="stat"><strong>{miles(s["totalNm"])}</strong><span>millas náuticas navegadas</span></div>'
            f'<div class="stat"><strong>53</strong><span>días, del 3 de enero al 24 de febrero</span></div>'
            f'<div class="stat"><strong>{lat}°S</strong><span>latitud más austral</span></div>'
            f'<div class="stat"><strong>22/1</strong><span>homenaje al ARA «Alférez Sobral»</span></div></div>')


def build_index(track):
    phases = "".join(f'<tr><th scope="row">{ph["name"]}</th><td>{miles(ph["nm"])} MN</td></tr>' for ph in track["summary"]["phases"])
    parts = [
        ("Antecedentes", "1982: el ingreso al Liceo Naval con la XXXV, el transporte ARA «Cabo de Hornos» y el Atlantis.", "./pages/antecedentes.html"),
        ("Sudor I", "Poner el velero en condiciones para el viaje.", "./pages/velero.html"),
        ("El mar", "Del Centro Naval Núñez a la costa patagónica y el cruce.", f"./pages/bitacora/{CHAPTERS[0]['slug']}.html"),
        ("Lágrimas", "El homenaje al Sobral, Tumbledown y Darwin.", "./pages/sobral.html"),
        ("Sudor II", "Odiseo y el regreso a Ítaca.", f"./pages/bitacora/{CHAPTERS[STAGES[2][2]]['slug']}.html"),
    ]
    journey = "".join(f'<a class="journey-card{" journey-card-featured" if n == "Lágrimas" else ""}" href="{h}"><span>0{k}</span><strong>{n}</strong><small>{d}</small></a>'
                      for k, (n, d, h) in enumerate(parts, 1))
    main = f"""<main id="contenido">
<section class="hero"><div class="shell hero-grid"><div class="hero-copy">
<p class="eyebrow">{SUBTITLE}</p>
<h1>Agua salada</h1>
<p class="lead">«El agua salada lo cura todo, ya sea en sus formas de sudor, de lágrimas o en el mar». Una travesía en velero desde Buenos Aires hasta Malvinas para rendir homenaje al aviso ARA «Alférez Sobral» y navegar las aguas que había navegado el transporte ARA «Cabo de Hornos».</p>
<div class="hero-actions"><a class="button" href="./pages/bitacora/index.html">Leer la bitácora</a><a class="text-link" href="./pages/sobral.html">El homenaje <span aria-hidden="true">→</span></a><a class="text-link" href="./cartografia.html">El recorrido <span aria-hidden="true">→</span></a></div>
{stats(track)}
</div>
<figure class="hero-media"><img src="./assets/images/charla/d02-image2.jpg" alt="Navegando a vela hacia Malvinas" fetchpriority="high"><figcaption>Rumbo a Malvinas · enero de 2024</figcaption></figure>
</div></section>
<section class="shell"><div class="memorial"><p class="eyebrow">Lágrimas · 22 de enero de 2024</p><h2>«Misión cumplida»</h2>
<p>Frente a la costa norte de las islas, la tripulación del Cabo de Hornos rindió honores al aviso ARA «Alférez Sobral», a su comandante, el capitán de corbeta Sergio Raúl Gómez Roca, y a los hombres que cayeron con él en mayo de 1982. Cuando la corona flotaba por la popa, dos toninas overas saltaron, una a cada lado.</p>
<p><a class="button" style="background:#fff;color:var(--navy)" href="./pages/sobral.html">Conocer la historia y ver la ceremonia</a></p></div></section>
{timeline(0)}
<section class="journey-overview shell" aria-labelledby="ruta-viaje"><div class="journey-heading"><div><p class="eyebrow">Sudor, lágrimas y mar</p><h2 id="ruta-viaje">El viaje en cinco partes</h2></div>
<p>Como en la charla, el relato va de los antecedentes al regreso.</p></div><div class="journey-cards">{journey}</div></section>
<section class="shell video-section"><div class="section-heading video-heading"><div><p class="eyebrow">Video</p><h2>Agua salada</h2></div><p>Navegando hacia las islas, la mañana del 22 de enero.</p></div>
{video("navegando-a-malvinas", 0, True)}<a class="gallery-link" href="./pages/videos.html">Ver todos los videos →</a></section>
<section class="shell"><article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Sobre la carta</p><h2>El recorrido completo</h2></header>
<p>El inReach del velero registró la posición durante toda la travesía. La cartografía permite seguirla día por día.</p>
<table class="nm-table"><tbody>{phases}<tr><th scope="row">Total</th><td>{miles(track["summary"]["totalNm"])} MN</td></tr></tbody></table>
<a class="gallery-link" href="./cartografia.html">Abrir la cartografía interactiva →</a></article></section>
</main>"""
    (ROOT / "index.html").write_text(
        page(0, "index.html", f"{SITE} · Velero Cabo de Hornos a Malvinas", "Travesía del velero Cabo de Hornos a Malvinas en 2024 y homenaje al ARA Alférez Sobral.", main,
             extra_head=NM_STYLE), encoding="utf-8")


NM_STYLE = ("<style>.nm-table{width:100%;max-width:520px;margin-top:1.2rem;border-collapse:collapse}.nm-table th,.nm-table td{padding:.5rem .7rem;border-bottom:1px solid var(--line);text-align:left}"
            ".nm-table td{text-align:right;color:var(--navy);font-weight:800}.nm-table tr:last-child th,.nm-table tr:last-child td{font-weight:800;border-bottom:0}</style>")


def build_antecedentes():
    main = f"""<main class="shell" id="contenido">
<section class="page-hero chapter-hero"><p class="eyebrow">Antecedentes</p><h1>Antes del agua salada</h1>
<p class="lead">El Liceo Naval, una promoción de amigos, el Atlantis en la Antártida y un transporte de la Armada que se llamaba como el velero.</p></section>
{draft("completar con tu relato de la charla; los epígrafes vacíos se pueden llenar en scripts/build_site.py.")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Antecedente I</p><h2>El Liceo Naval y la XXXV</h2></header>
<p>Todo empieza en el Liceo Naval Militar «Almirante Guillermo Brown». Ricardo ingresó en 1982, el mismo año de la guerra de Malvinas, con la XXXV promoción, la de los amigos que siguen navegando juntos.</p><p>Por eso el banderín de la XXXV tiene a las Malvinas como motivo. Cuarenta y dos años después, aquel cadete que entró al Liceo con la guerra de fondo llegó navegando hasta las islas.</p></article>
{photo_grid("liceo", 1, "Liceo Naval y la XXXV")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Antecedente I</p><h2>El Atlantis y la Antártida</h2></header>
<p>Antes de Malvinas hubo otra gran travesía: la expedición del velero Atlantis desde Buenos Aires hasta la Antártida, entre 2021 y 2022.</p>
<a class="gallery-link" href="{ATLANTIS}" target="_blank" rel="noopener noreferrer">Ver el sitio de Atlantis al fin del mundo ↗</a></article>
{photo_grid("atlantis", 1, "Atlantis")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Antecedente II</p><h2>El transporte ARA «Cabo de Hornos»</h2></header>
<p>El transporte ARA B-5 «Cabo de Hornos», de la clase Costa Sur, se construyó en el astillero Príncipe, Menghi y Penco: 119,9 metros de eslora y 10.894 toneladas de desplazamiento. Su quilla se puso en 1977, fue botado en 1978 y entró en servicio en 1979.</p>
<p>Durante la guerra de Malvinas lo comandaba el entonces capitán de corbeta Ricardo Ángel Franzosi, padre de Ricardo. En esos meses fue buque logístico: transportó tropa y pertrechos.</p><p>Al terminar la guerra, el «Cabo de Hornos» trajo desde Francia los aviones Super Étendard de la Armada.</p>
<p>Cuarenta y dos años después, su hijo llevó otro «Cabo de Hornos», un velero, a navegar las mismas aguas que su padre había navegado.</p>
</article>
{photo_grid("transporte", 1, "Transporte ARA Cabo de Hornos")}
{photo_grid("familia", 1, "")}
</main>"""
    (ROOT / "pages" / "antecedentes.html").write_text(
        page(1, "pages/antecedentes.html", f"Antecedentes · {SITE}", "Los antecedentes de la travesía: el Liceo Naval, la XXXV, el Atlantis y el transporte ARA Cabo de Hornos.", main), encoding="utf-8")


def build_velero():
    main = f"""<main class="shell" id="contenido">
<section class="page-hero chapter-hero"><p class="eyebrow">Sudor I</p><h1>El velero Cabo de Hornos</h1>
<p class="lead">Siete años entre la compra y la primera singladura: la carroza nueva, la pintura, el motor, los interiores y todo lo necesario para llevar el barco al Atlántico Sur.</p></section>
{draft("completar con la ficha del velero (eslora, astillero, año, motor).")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">2017 · 2019 · 2024</p><h2>De casco azul a «Cabo de Hornos»</h2></header>
<p>El velero llegó en 2017, después de la compra, con el casco azul que se ve en las primeras fotos. Estuvo en tierra hasta 2019, mientras Jesús Vinacua le hacía las modificaciones de la carroza.</p>
<p>Desde 2019 hasta 2024 se preparó para su primera singladura: pintura, motor nuevo, instalaciones, interiores y cada detalle que exige una navegación al Atlántico Sur. Esa singladura fue la travesía a Malvinas.</p></article>
<section class="video-grid">{video("preparativos", 1, True)}</section>
{photo_grid("sudor1", 1, "El velero Cabo de Hornos")}
{photo_grid("sudor1b", 1, "Preparativos del velero")}
<nav class="chapter-nav" aria-label="Capítulos"><a href="./antecedentes.html"><span>Anterior</span><strong>Antecedentes</strong></a><a href="./bitacora/{CHAPTERS[0]['slug']}.html"><span>Siguiente</span><strong>{CHAPTERS[0]['title']}</strong></a></nav>
</main>"""
    (ROOT / "pages" / "velero.html").write_text(
        page(1, "pages/velero.html", f"El velero · {SITE}", "El velero Cabo de Hornos y su preparación para la travesía a Malvinas.", main), encoding="utf-8")


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
<section class="page-hero chapter-hero"><p class="eyebrow">Lágrimas · Gloria y honor a los muertos por la Patria</p><h1>Homenaje al ARA «Alférez Sobral»</h1>
<p class="lead">Ceremonia naval en homenaje al capitán Gómez Roca y a la tripulación del aviso ARA «Sobral», el 22 de enero de 2024, frente a la costa norte de Malvinas.</p></section>
<section class="video-grid" aria-label="Video de la ceremonia">{video("ceremonia-sobral", 1, True)}</section>
<section class="memorial"><p class="eyebrow">22 de enero de 2024 · 19.30 h</p><h2>La ceremonia en el mar</h2>
<p>El velero navegaba hacia Cape Dolphin con 20 a 24 nudos del oeste. Al llegar a la posición elegida, la tripulación formó en cubierta, se rindieron los honores correspondientes y se arrojó una corona al mar.</p>
<p>Mientras tanto, un grupo de toninas overas y delfines se acercó al barco. Cuando la corona flotaba por la popa, dos toninas saltaron, una a cada lado.</p>
<p>Esa misma noche salió el mensaje por el inReach: «Ceremonia de rendición de honores a los caídos del aviso ARA Sobral, realizada. Cumpliendo los deseos de los compañeros de la promoción 90 de la ESNM».</p></section>
{photo_grid("el-homenaje", 1, "Ceremonia en homenaje al ARA Sobral")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">El aviso</p><h2>El ARA «Alférez Sobral»</h2></header>
<p>El aviso ARA «Alférez Sobral» (A-9) había sido el remolcador de flota USS «Salish» (ATA-187), botado en 1944 en Orange, Texas, e incorporado a la Armada Argentina en 1972. Llevaba el nombre del alférez José María Sobral, el primer marino argentino que invernó en la Antártida.</p>
<p>El sábado 1 de mayo de 1982 un Canberra de la Fuerza Aérea fue derribado a unas 100 millas al norte del estrecho de San Carlos, y el «Sobral», que operaba en la zona, recibió la orden de buscar y rescatar a sus dos tripulantes.</p>
<p>A los 30 minutos del 3 de mayo fue detectado por unidades navales británicas. Al aparecer los helicópteros, el comandante, capitán de corbeta Sergio Raúl Gómez Roca, ordenó cubrir puestos de combate, y la tripulación abrió fuego con el cañón de 40 mm y las ametralladoras de 20 mm. Los helicópteros atacaron con misiles Sea Skua. Para proteger a su gente, Gómez Roca ordenó desalojar las cubiertas superiores y se quedó en el puente solo con los hombres indispensables.</p>
<p>A la 01.20 un misil destruyó por completo el puente de comando y el cuarto de radio que estaba debajo. Murieron el comandante y quienes estaban allí: ocho muertos y ocho heridos.</p>
<p>Herido en una pierna, el segundo comandante, teniente de navío Sergio Bazán, asumió el mando de un buque sin puente, sin cartas, sin radio, con el timón averiado y un incendio a bordo. Navegando con brújulas terrestres y la rosa de un compás rescatado, el «Sobral» llegó a Puerto Deseado la noche del 5 de mayo. Su puente destruido se conserva hoy en el Museo Naval de la Nación, en Tigre.</p>
<p class="source-note">Fuente: <a href="https://www.argentina.gob.ar/armada/ataque-al-aviso-ara-alferez-sobral" target="_blank" rel="noopener noreferrer">Armada Argentina, «Ataque al Aviso ARA Alférez Sobral»</a>.</p></article>
<section class="memorial"><p class="eyebrow">Los caídos · 3 de mayo de 1982</p><h2>Gloria y honor</h2>
<ul class="fallen-list"><li>Sergio Raúl Gómez Roca<small>Capitán de corbeta · Comandante</small></li><li>Claudio Olivieri<small>Guardiamarina</small></li><li>Mario Alancay<small>Cabo principal</small></li><li>Daniel Tonina<small>Cabo segundo</small></li><li>Sergio Medina<small>Cabo segundo</small></li><li>Ernesto Del Monte<small>Cabo segundo</small></li><li>Héctor Dufrechou<small>Marinero</small></li><li>Roberto D’Errico<small>Conscripto</small></li></ul>
<p>Y un ruego por la tripulación del ARA «San Juan», en patrulla permanente en el Mar Argentino.</p></section>
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">El pedido</p><h2>La Promoción 90 y el transporte «Cabo de Hornos»</h2></header>
<p>La ceremonia fue un pedido de los compañeros de la Promoción 90 de la ESNM. Gracias a ellos, por concedernos el honor de hacerlo.</p>
<p>La historia tenía además un hilo familiar: durante la guerra, el padre de Francho comandaba el transporte ARA «Cabo de Hornos». Desde el mar, Francho lo escribió así:</p>
{q("Alguna vez papá contó que estaba navegando cerca y quiso ir a auxiliar al Sobral con el \"Cabo de Hornos\" y no lo dejaron... Creo que si vio esto desde arriba estará contento que el \"Cabo de Hornos\" pudo ir a ver así compañero. Gracias por permitirnos ser parte de vuestro homenaje a su compañero. Será un honor que atesoraremos en nuestro corazón toda la vida!", "22 de enero de 2024")}
<p>Al regreso, el 24 de febrero, en el muelle esperaban la familia y los compañeros de promoción de su padre.</p></article>
{photo_grid("sobral", 1, "Promoción 90")}
<article class="card prose page-card"><header class="article-heading"><p class="eyebrow">Dónde</p><h2>La posición de la ceremonia</h2></header>
<p>Al norte del archipiélago, en la derrota hacia Cape Dolphin. La línea muestra el recorrido del velero entre el 20 y el 23 de enero.</p><div id="mapa-sobral" role="region" aria-label="Mapa de la posición de la ceremonia"></div>
<a class="gallery-link" href="./bitacora/tumbledown-y-darwin.html">Seguir con Tumbledown y Darwin →</a></article>
</main>"""
    (ROOT / "pages" / "sobral.html").write_text(
        page(1, "pages/sobral.html", f"Homenaje al ARA Alférez Sobral · {SITE}",
             "Ceremonia naval del velero Cabo de Hornos en homenaje al aviso ARA Alférez Sobral y al capitán Gómez Roca, enero de 2024.",
             main, extra_head=leaflet, scripts=scripts), encoding="utf-8")


def build_gracias():
    rows = "".join(f'<div><dt>{html.escape(a)}</dt><dd>{html.escape(b)}</dd></div>' for a, b in THANKS)
    main = f"""<main class="shell" id="contenido">
<section class="page-hero chapter-hero"><p class="eyebrow">Gracias</p><h1>Muchas gracias</h1>
<p class="lead">A quienes nos recibieron, nos ayudaron y nos siguieron desde tierra.</p></section>
<article class="card prose page-card"><dl class="specs thanks">{rows}</dl>
<p>Y a la Promoción 90 de la ESNM, por concedernos el honor del homenaje, y a todos los que siguieron el viaje mensaje a mensaje.</p></article>
{photo_grid("gracias", 1, "Agradecimientos")}
</main>"""
    (ROOT / "pages" / "gracias.html").write_text(
        page(1, "pages/gracias.html", f"Gracias · {SITE}", "Agradecimientos de la travesía del velero Cabo de Hornos a Malvinas.", main,
             extra_head="<style>.thanks dd{text-align:right;max-width:60%;font-weight:600}</style>"), encoding="utf-8")


def build_videos():
    cards = "".join(video(v, 1, featured=(v == "ceremonia-sobral")) for v in
                    ["ceremonia-sobral", "navegando-a-malvinas", "zarpada", "rumbo-a-puerto-belgrano", "el-cruce",
                     "tumbledown", "darwin-1", "darwin-2", "darwin-3", "preparativos", "regreso-1", "regreso-2"])
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">Videos</p><h1>El viaje en movimiento</h1>'
            f'<p class="lead">La ceremonia del Sobral, el cruce, las islas y el regreso.</p></section>'
            f'<section class="video-grid">{cards}</section></main>')
    (ROOT / "pages" / "videos.html").write_text(page(1, "pages/videos.html", f"Videos · {SITE}", "Videos de la travesía del velero Cabo de Hornos a Malvinas.", main), encoding="utf-8")


def build_gallery():
    sections = [("Antecedentes", ["liceo", "atlantis", "transporte", "familia"]), ("Sudor I: el velero", ["sudor1", "sudor1b"])]
    sections += [(ch["title"], [ch["slug"]] + ch.get("extra_photos", []) + (["tumbledown"] if ch["slug"] == "tumbledown-y-darwin" else [])) for ch in CHAPTERS]
    sections += [("Promoción 90", ["sobral"]), ("Gracias", ["gracias"])]
    body = "".join(f'<section class="gallery-section"><h2>{html.escape(t)}</h2>{"".join(photo_grid(k, 1, t) for k in keys)}</section>'
                   for t, keys in sections if any(PHOTOS.get(k) for k in keys))
    main = (f'<main class="shell" id="contenido"><section class="page-hero chapter-hero"><p class="eyebrow">Galería</p><h1>Fotos de la travesía</h1>'
            f'<p class="lead">Las imágenes de la charla «Agua salada», ordenadas como el viaje.</p></section>{body}</main>')
    (ROOT / "pages" / "gallery.html").write_text(
        page(1, "pages/gallery.html", f"Galería · {SITE}", "Galería de fotos de la travesía del velero Cabo de Hornos a Malvinas.", main,
             extra_head="<style>.gallery-section h2{margin:1.5rem 0 1rem}</style>"), encoding="utf-8")


CARTO_JS = r"""
const map=L.map('map',{scrollWheelZoom:false});
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:12,attribution:'&copy; OpenStreetMap contributors'}).addTo(map);
const palette={ida:'#237887',malvinas:'#7256a5',regreso:'#c47743'};const names={ida:'rumbo al sur',malvinas:'Malvinas',regreso:'regreso'};
const status=document.getElementById('map-status');const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>new Intl.DateTimeFormat('es-AR',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(v+'T12:00:00Z'));
const data=window.TRACK;let dayIndex=data.days.length-1,layerMode='full',mapLayer=L.featureGroup(),currentMarker,playing=false,playTimer;
const draw=(fit=true)=>{map.removeLayer(mapLayer);mapLayer=L.featureGroup().addTo(map);const visible=data.days.slice(0,dayIndex+1).filter(d=>layerMode==='full'||d.phase===layerMode);let nm=0;
visible.forEach(d=>{if(d.points.length>1)L.polyline(d.points,{color:palette[d.phase],weight:4,opacity:.9,lineJoin:'round'}).addTo(mapLayer);nm+=d.nm;});
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
            + NM_STYLE + "<style>.timeline-card{display:grid}</style>")
    scripts = f'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script><script src="./data/track.js"></script><script>{CARTO_JS}</script>'
    (ROOT / "cartografia.html").write_text(
        page(0, "cartografia.html", f"Cartografía · {SITE}", "Recorrido día por día del velero Cabo de Hornos en su travesía a Malvinas.", main, head, scripts), encoding="utf-8")


def main():
    track = load_track()
    build_cartografia(track)
    build_chapters(track)
    build_bitacora_index(track)
    build_index(track)
    build_antecedentes()
    build_velero()
    build_sobral(track)
    build_gracias()
    build_videos()
    build_gallery()
    print(f"Sitio generado: {len(CHAPTERS)} capítulos · {miles(track['summary']['totalNm'])} MN")


if __name__ == "__main__":
    main()
