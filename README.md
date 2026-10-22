# Agua salada

Sitio de la travesía del velero **Cabo de Hornos** desde Buenos Aires hasta Malvinas (enero y febrero de 2024) y del homenaje al aviso **ARA «Alférez Sobral»** y a sus caídos.

Sigue la estructura de la charla «Agua salada»: antecedentes, sudor, mar, lágrimas, el regreso y los agradecimientos.

## Cómo se genera

- `python scripts/build_track.py "<explore.gpx>"` arma `data/track.js` con el recorrido del Garmin inReach, depurado y medido en millas náuticas.
- `python scripts/build_site.py` genera todas las páginas. Los textos, las fotos y los epígrafes están en ese script.

Las fotos están en `assets/images` y los videos, convertidos a H.264, en `assets/videos`. El sitio se publica con GitHub Pages (`.github/workflows/pages.yml`).
