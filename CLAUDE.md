# Ebisu — memoria del proyecto

Segundo bot de trading del propietario, con activos **que NO son cripto**. El primero es Ploutos
(repositorio privado aparte, cripto spot, sigue en marcha; ruta local en `CLAUDE.local.md`): **de Ploutos solo se
lee; nunca se toca nada**.

**Este repositorio es PUBLICO** (`github.com/jlbou/ebisu`). Ver "Repositorio publico" mas abajo.

**Estado (13/10/2026): estudios 1 y 2 sin ganadora** (reserva 2015-2026 ya usada: `docs/estudios/estudio2-reserva.md`).
H2 tambien probada en la reserva de divisas: no pasa. Se aplica `docs/decisiones/12-si-no-pasa.md`: estudio 3 posible solo con datos anteriores al 2000; red de seguridad, el bot del indexado.

## La leccion de Ploutos que manda aqui

En Ploutos se construyo toda la infraestructura antes de tener una estrategia con ventaja; tras ~30 estudios, ninguna
estrategia de operar activamente ganaba. La unica que vale la pena es "L" (rotacion semanal de tendencia con medias de
20/50/100/200 dias): protege mucho en las caidas, pero en el anyo de prueba limpia perdio un 7 % (BTC, un 22 %).

**Por eso Ebisu va al reves, en este orden, y no se salta ningun paso:**

1. **Decisiones de fondo** (del propietario): mercado, capital, apalancamiento si o no (y el maximo tolerable), broker y
   regulacion en Espanya, objetivo, tiempo de dedicacion. Cada una queda escrita en `docs/decisiones/`.
2. **Estrategia probada con la historia**, con el criterio fijado y subido a git ANTES de medir: exploracion, reserva
   sin mirar (se usa UNA sola vez, al final) y prueba final; un liston contra la suerte (Sharpe deflactado) cuando se
   prueban muchas variantes. Cada variante probada se cuenta.
3. **Solo si alguna estrategia pasa**, construir el bot, reaprovechando lo que se pueda de Ploutos (reglas duras, motor
   de riesgo, papel, jueces, panel, Telegram), copiado y adaptado aqui, nunca importado desde alli.

## Convenciones de trabajo

- **Con el propietario, en catalan** y con explicaciones sencillas. **Codigo, commits, documentos y logs, en castellano.**
- **Paso a paso:** una decision por mensaje, con opciones y la recomendada marcada. No empezar el paso siguiente sin
  el OK del propietario.
- **Las decisiones de capital, apalancamiento, riesgo y dinero son del propietario.** Llevarle la contraria con argumentos
  cuando haga falta; no decidir por el.
- **Nada de dinero real ni claves** sin que el propietario lo decida. **Secretos solo en `.env`** (en `.gitignore`; un
  `.env.example` sin valores): los pone el propietario y **nunca se le pide que pegue un token**. Nunca `source .env`.
- **Imagen:** en la UI y en Telegram nunca se nombra a Claude: "la IA" o "el analista".
- **Estudios** (`docs/estudios/`): el criterio se fija y se sube ANTES de medir; lo que no se ha comprobado se dice;
  fuentes con enlace y fecha de lectura. Un estudio no toca el bot.
- **Verificar, no suponer** lo que dependa de un broker, una API o la normativa.
- **No anyadir nada** fuera de lo decidido: decirselo al propietario con argumentos.
- **Kronos** (modelo de prediccion de velas): el entorno y los pesos estan en `var/kronos/` del repositorio de Ploutos
  (~860 MB), guardados para Ebisu. **No borrarlos.** En cripto no acerto (`Ploutos/docs/estudios/kronos/`); aqui se
  probaria con la misma prueba limpia, criterio antes.
- **Skills** (11/10: solo cuando sean utiles de verdad, no por usarlas):
  - `process-interviewer`: para el paso 1 entero (las decisiones de fondo), respetando una decision por mensaje, con
    opciones y la recomendada marcada.
  - `council`: solo para las decisiones mas dificiles: el mercado y el apalancamiento.
  - Mas adelante, si hacen falta: `literature-review` (pruebas academicas, paso 2), `data:statistical-analysis`
    (mediciones, paso 2), `superpowers` (construir el bot, paso 3). `deep-research` lanza subagentes (caro): solo si
    el propietario lo pide.
- **Repositorio publico (decision del 12/10):** todo lo que entra en git se puede leer en internet.
  - **Nunca** en git: el nombre ni el correo personal del propietario, rutas de su ordenador, datos del servidor
    (IP, nombres de Tailscale, proveedor), claves, saldos reales ni detalles de su vida. Se escribe "el propietario".
  - Lo personal va en **`CLAUDE.local.md`** (se carga solo en cada sesion) o en **`privado/`**: los dos, en
    `.gitignore`.
  - Autor de los commits: `jlbou <292183709+jlbou@users.noreply.github.com>` (configurado en el repo).
  - Antes de cada commit, mirar el diff buscando datos personales. Licencia MIT.
- **Stack:** Python 3.12 en `.venv/` (`.venv/Scripts/python.exe`), dependencias fijadas en `requirements.txt`
  (pandas, yfinance). Dependencia nueva = justificarla antes. Datos descargados, en `var/` (fuera de git).
  En Git Bash, `python` a secas abre el de la tienda de Windows y se queda colgado: usar siempre la ruta del venv.
- **Pruebas:** `.venv/Scripts/ruff.exe check .` y `.venv/Scripts/python.exe -m pytest -q` (las validaciones con datos
  inventados) ANTES de cada commit con codigo. GitHub las repite en cada push (`.github/workflows/pruebas.yml`).
- **Formato de commit (fijo).** Las secciones opcionales se omiten ENTERAS si no aplican.

  ```
  <ambito>: <que se ha hecho, en minuscula, max 72 caracteres>

  QUE CAMBIA
  - una linea por pieza tocada, en orden de importancia

  POR QUE
  Parrafo corto. Si corrige algo, primero el sintoma y luego la causa.

  HALLAZGOS                  (opcional)
  1. ...

  MEDIDO                     (opcional: los numeros, con el tamanyo de la muestra)

  TESTS: N en verde          (opcional, cuando haya codigo)

  Co-Authored-By: <el modelo que hace el commit> <noreply@anthropic.com>
  ```
  Ambitos: `docs`, `decision`, `estudio`, `fase N`, `fix`, `tests`. En Windows, el mensaje con `git commit -F <fichero>`.

## Lo que ya se sabe (de Ploutos, `docs/estudios/viabilidad-otros-activos.md`, 06/10/2026, comisiones de IBKR)

- **Divisas:** el mercado mas grande y eficiente; suma cero menos costes. Sin apalancamiento se mueven ~7-10 % al anyo
  (un par mayor); hacen falta ~10.000 € para que el minimo de 2 $ por orden no pese. Con apalancamiento (CFD), pierden
  el 70-90 % de los minoristas (CNMV).
- **ETF europeos e indices:** sin apalancamiento, viables con ~1.000-5.000 € operando poco (semanal o mensual). Seguir
  la tendencia tiene decadas de pruebas academicas en bolsa, bonos, oro y materias primas. Un minorista de la UE no
  puede comprar ETF de EE. UU.
- **Acciones:** sin apalancamiento, ~1.250-3.000 € por posicion (minimo de 1,25-3 € por orden). Hacienda: vender con
  perdida y recomprar el mismo valor en dos meses aplaza la perdida (art. 33.5 LIRPF).
- **Oro:** al contado, en teoria sin apalancamiento (sin comprobar si una cuenta de la UE puede); en futuros, siempre
  apalancado.
- **CFD y futuros:** siempre apalancados. En Espanya esta prohibido anunciar CFD a minoristas (CNMV, 11/07/2023). El
  apalancamiento no crea ventaja: multiplica lo que hay.
- **Con 50 € nada es viable sin apalancamiento:** las comisiones se comen el 3-13 % de cada operacion.

## Decisiones del propietario

| Fecha | Decision | Documento |
|---|---|---|
| 11/10/2026 | Empezar Ebisu por las decisiones de fondo; la primera, el mercado | este fichero |
| 11/10/2026 | Skills: `process-interviewer` para el paso 1 y `council` para mercado y apalancamiento (opcion A) | este fichero |
| 11/10/2026 | **Objetivo: ganar dinero, cuanto mas mejor.** Pasa una estrategia que gane mas que un indexado mundial mantenido, o lo mismo con claramente menos caida, neto de comisiones e impuestos (opcion A) | `docs/decisiones/01-objetivo.md` |
| 12/10/2026 | **Mercado: bolsa, bonos y oro siguiendo la tendencia**; el vehiculo (ETF o fondos con traspasos) se decide con el broker; la idea de una persona conocida (rango del dia anterior en divisas) entra en las hipotesis (opcion A, tras el council) | `docs/decisiones/02-mercado.md`, `docs/hipotesis.md` |
| 12/10/2026 | **Capital maximo: 250 €** (por ahora); con eso los ETF de IBKR no son viables por comisiones | `docs/decisiones/03-capital.md` |
| 12/10/2026 | **Vehiculo: se decide en el paso 2** probando fondos con traspasos y ETF fraccionados sin comision; el propietario prefiere que todo sea automatico (opcion C) | `docs/decisiones/04-vehiculo.md` |
| 12/10/2026 | **Sin apalancamiento (1x), regla dura** (codigo y sin margen en el broker); el estudio calcula el apalancado solo como informacion; el apalancamiento nunca rescata un resultado justo (opcion B, tras el council) | `docs/decisiones/05-apalancamiento.md` |
| 12/10/2026 | **Tiempo: sin ritmo fijo** mientras se hace; cuando funcione, que el propietario no tenga que hacer nada (opcion C) | `docs/decisiones/06-tiempo.md` |
| 12/10/2026 | **Lista cerrada de hipotesis** (si ninguna pasa, indexado sin bot); los 250 € no se necesitan en 3 anyos; sin aportaciones periodicas | `docs/decisiones/07-cierre-paso-1.md` |
| 12/10/2026 | **IA como analista con freno:** explica cada mes y puede reducir o aplazar compras, nunca anyadir riesgo; el filtro se prueba en papel contra el bot sin IA (opcion A) | `docs/decisiones/08-ia.md` |
| 12/10/2026 | **Criterio del estudio 1 APROBADO** (por partes): exploracion 2001-2014, reserva 2015-2026; H1 en 4 variantes y H2 en los 7 pares principales (N = 5); Kronos fuera; costes, impuestos al 19 % y referencia (indexado mantenido); umbrales | `docs/diseno-estudio-1.md` |
| 12/10/2026 | **Identidad y panel:** logo cana-grafico con anzuelo en verde mar; social preview; panel de una pagina tipo informe con 6 secciones (solo disenyo, se construye si una estrategia pasa) | `docs/decisiones/09-identidad-y-panel.md`, `assets/logo/` |
| 12/10/2026 | **Telegram (solo disenyo):** 7 tipos de mensaje (con un todo bien semanal), comandos /estado, /detalle, /pausa y /reanudar; mensajes cortos | `docs/decisiones/10-telegram.md` |
| 13/10/2026 | **Papel (fijado antes de medir):** semanal 3 meses, mensual 6; pasa con fidelidad al simulador, sin incidencias, sin caer mas que la peor caida historica y con el si del propietario; el freno de la IA en sombra hasta 5 casos con acierto medio | `docs/decisiones/11-papel.md` |
| 13/10/2026 | **Estudio 1: NO PASA NINGUNA** (H1 protege pero no supera el liston contra la suerte; H2 pierde). Reserva sin tocar | `docs/estudios/estudio1-exploracion.md` |
| 13/10/2026 | **Criterio del estudio 2 APROBADO:** E2 (9 activos, pesos por riesgo, mensual, banda de 2 puntos) y H1-F a la reserva 2015-2026, una vez; pasan con 1, 2 y Sharpe probabilistico >= 0,95 cada una; si ninguna pasa, se cierra Ebisu (cambiado por la decision 12) | `docs/diseno-estudio-2.md`, `docs/estudios/recerca-mejoras.md` |
| 13/10/2026 | **Si la reserva del estudio 2 no da ganadora (antes de medir):** estudio 3 con un enfoque distinto, escrito antes, solo con datos anteriores al 2000 y liston mas alto; y Ebisu como bot del indexado como red de seguridad (opcion A + C) | `docs/decisiones/12-si-no-pasa.md` |
| 13/10/2026 | **Estudio 2: NO PASA NINGUNA** en la reserva: E2 1,59 % (caida 8,9 %, confianza 0,851) y H1-F 2,64 % (14,7 %, 0,928) frente al indexado ~10,5 % (33,6 %) | `docs/estudios/estudio2-reserva.md` |
| 13/10/2026 | **H2 en la reserva de divisas (2015-2026, criterio antes): NO PASA**, pierde un 6,01 % al anyo (caida 51,8 %) y pierde en los 7 pares; H2 descartada del todo | `docs/diseno-h2-reserva.md`, `docs/estudios/h2-reserva.md` |
| 13/10/2026 | **H2 con el orden real de las horas (solo informacion): sigue perdiendo** en los dos tramos, tambien en el mejor caso (2015-2026: -2,9 % a -3,9 % al anyo); idea cerrada | `docs/estudios/h2-horas.md` |

## Pendiente

- **Paso 1 CERRADO (12/10): `docs/prd-paso-1.md`.** Verificaciones hechas (`docs/estudios/verificaciones-vehiculo.md`):
  con fondos no hay oro (solo mineras) ni API; Trading 212 (probablemente la alemana, BaFin) tiene API y ETF en euros
  sin comision. Inventario hecho (ventana comun desde 2000). **Criterio del estudio 1 aprobado**; siguiente: bajar
  BCE, Dukascopy y la segunda fuente y montar las series en euros (`docs/diseno-estudio-1.md` 7). Faltan
  dos puntos en la app o el demo de Trading 212 (cuenta abierta, esperando la verificacion de identidad).
- **Trading 212 (12/10):** sin cuenta demo para Trading 212 EU; preguntas de la API (tipos de orden, fracciones, clave de
  solo lectura, limites, tasa italiana del oro) enviadas a un agente del chat: respuesta en 1 dia habil. Anotarla en
  `docs/estudios/verificaciones-vehiculo.md` 5.6.
- **Dukascopy: COMPLETO (13/10 05:30)** y contrastado con el BCE (pasa; seccion 9 del criterio). Siguiente: medir la
  exploracion con `medir.py --exploracion --confirmo` (una sola vez), cuando el propietario lo diga.
- **Clave para el paso 2:** los impuestos cuentan operacion por operacion, y la referencia es el indexado con
  traspasos (`docs/decisiones/02-mercado.md`).
