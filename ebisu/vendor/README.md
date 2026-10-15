# Librerias de terceros del panel

En el repositorio a proposito: el panel solo se ve por Tailscale y no pide nada a Internet. Sin dependencias nuevas de
Python: son ficheros que sirve `ebisu/servidor.py`.

| Fichero | Que es | Version | Origen | SHA-256 (base64) | Licencia |
|---|---|---|---|---|---|
| `lightweight-charts.standalone.production.js` | Lightweight Charts, de TradingView: los graficos interactivos | 5.2.1 | copia del de Ploutos (paquete npm `lightweight-charts`), misma huella que alli | `4hzFyqAibvML2FScULnvkmYV8qTua05IY1NHelX1mM8=` | Apache-2.0 (cabecera del fichero) |
| `atkinson-hyperlegible-latin-400-normal.woff2` | Atkinson Hyperlegible 400 (texto) | 5.3.0 | paquete npm `@fontsource/atkinson-hyperlegible`, via cdn.jsdelivr.net, 15/10/2026, permiso del propietario | `1kuoOO9UcruiSGIOxP2LWqfPDbKQjguyMGAMryebp7w=` | SIL OFL 1.1 (`LICENSE-atkinson-hyperlegible.txt`) |
| `atkinson-hyperlegible-latin-700-normal.woff2` | Atkinson Hyperlegible 700 (titulos y cifras) | 5.3.0 | idem | `FA4r0lpzFcigYlCDkUJrDYwyl0AMlHuNhHvij3OhmfA=` | SIL OFL 1.1 |

La letra la eligio el propietario el 15/10/2026 (plan de disenyo del panel, skill `frontend-design`): pensada para leerse
bien, sobre todo las cifras y en pantallas pequenyas, y distinta de la de Ploutos.
