# Ebisu — memoria del proyecto

Segundo bot de trading del propietario, con activos **que NO son cripto**. El primero es Ploutos
(repositorio privado aparte, cripto spot, sigue en marcha; ruta local en `CLAUDE.local.md`): **de Ploutos solo se
lee; nunca se toca nada**.

**Este repositorio es PUBLICO** (`github.com/jlbou/ebisu`). Ver "Repositorio publico" mas abajo.

**Estado (15/10/2026): H1-M, bot en papel INSTALADO en el VPS y probado** (`docs/instalacion-bot.md`); 3 dias
sin incidencias (hasta el 18/10) y despues el propietario decide `--empezar` (primera senyal: 30/10/2026). Divisas:
laboratorio en papel con la IA, sin empezar.

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
| 13/10/2026 | **Estudio 3 de divisas con reglas por escenario + modelo + proteccion (5 capas).** El propietario prefiere divisas (no bolsa/bonos/oro). **Apalancamiento solo en divisas** (~4x, el minimo para 1.000 unidades), una posicion, calendario de eventos; pasa solo con el liston de riesgo M: P(perder la mitad en 3 anyos) < 3 %, caida < 30 %, estres < 25 % | `docs/decisiones/13-apalancamiento-divisas.md`, `docs/estudios/estudio3-opciones.md` |
| 14/10/2026 | **Diagnostico del estudio 3: NO PASA la puerta 1.** 27.315 operaciones en los 7 principales: las no marcadas pierden -0,11 % por operacion (mediana +0,16 %) y son el 34 %; todos los escenarios pierden parecido | `docs/estudios/estudio3-diagnostico.md` |
| 14/10/2026 | **Revision de la literatura de divisas** (tendencia desaparecida desde ~2009; carry no pasaria el liston M a 4x; fixings, el unico con margen) y **prueba rapida del fixing 2020-2026: NO SIGUE** (EUR/USD y USD/JPY, efecto por operacion de -0,4 a +0,6 pb frente a los 2,5 pb necesarios) | `docs/estudios/recerca-divisas-2.md`, `docs/estudios/fixing-rapido.md` |
| 14/10/2026 | **Replanteamiento (tras el council):** divisas solo en papel como laboratorio con la IA (A); los 250 € no van a un indexado; bolsa, bonos y oro desde cero: 4 tipos de mercado (bolsa sube/baja x inflacion alta/baja), se juzga 1971-2026 y ademas tiene que funcionar en 1990-2026 (A+) | `docs/decisiones/14-replanteamiento.md`, `docs/estudios/datos-antes-2000.md` |
| 14/10/2026 | **Plan del estudio 4 APROBADO** (bolsa, bonos y oro): una medicion 1971-2026 + 1990-2026, 5 variantes (H1-M, H1-F, + volatilidad, + fiscal, + modelo de scikit-learn solo en bolsa), N = 10, tipos de mercado, tramos reales del ahorro; dos revisiones (21 correcciones) | `docs/plan-estudio-4.md`, `docs/estudios/recerca-activos-2.md` |
| 14/10/2026 | **Estudio 4 (una medicion, 1971-2026): NO PASA NINGUNA.** H1 si pasa el liston contra la suerte (deflactado 0,97-0,98, Sharpe 0,48 frente a 0,36) y cae mucho menos (14-19 % frente al 58 %), pero gana 2-3 puntos menos al anyo (H1-F 6,50 %, H1-M 5,57 % frente al 8,50 %) y en los anyos de subida se queda 10-15 puntos atras. El modelo de scikit-learn no aporta (PBO 0,77). 1971-2026 queda visto | `docs/estudios/estudio4-veredicto.md` |
| 14/10/2026 | **Aceptar el intercambio de H1 (despues de ver el veredicto, dicho asi):** ganar menos a cambio de caer mucho menos; H1 no "pasa", pero no es suerte; va al papel hacia delante con la IA en sombra; nada mas se mide sobre 1971-2026 (opcion A) | `docs/decisiones/15-aceptar-h1.md` |
| 14-15/10/2026 | **Plan del bot en papel (H1-M):** precios de los 4 ETF en Yahoo (P1); el VPS de Ploutos pero aparte, con latido a Healthchecks (P2); RSS oficiales y de medios para la IA (P3); Telegram solo `/estado` y `/detalle`, pausa desde el panel (P4); panel antes del papel (P5); copia diaria al portatil, 7 dias (P6) | `docs/plan-bot-papel.md` 9 |
| 15/10/2026 | **IA del bot: copia propia y verificada** en `/opt/ebisu/bin` (la del VPS es de Ploutos y vive en `/home/ploutos`); sin tocar Ploutos (opcion A) | `docs/instalacion-bot.md` |
| 15/10/2026 | **Healthchecks coordinado con Ploutos:** 3 comprobaciones de Ebisu (`ebisu-dia`, `ebisu-copia`, `ebisu-copia-portatil`), cada URL solo en la maquina que late, mismo canal de avisos y etiqueta por bot; `ebisu-comandos` sin vigilar | `docs/instalacion-bot.md` |

## Pendiente

- **Bot en papel (H1-M), instalado el 15/10** (`docs/instalacion-bot.md`, `deploy/`): 3 dias sin incidencias hasta el
  18/10; revisar avisos y registros con el propietario y que decida `--empezar` (primera senyal: 30/10/2026). Despues,
  6 meses de papel (decision 11); la IA en sombra hasta 5 casos.
- **Trading 212** (solo si el papel pasa y se opera con dinero real): la respuesta del agente sobre la API ya esta en
  `docs/estudios/verificaciones-vehiculo.md` 5.6 (13/10) y la identidad ya esta verificada (5.5). El 15/10 (5.6 ter):
  API confirmada en su documentacion (4 tipos de orden, decimales, nunca por importe, ordenes no idempotentes: regla dura
  si hay dinero real) y la tasa italiana NO se aplica al oro (SGLD lo emite una sociedad irlandesa). Queda que el
  propietario mire en la app la bolsa y las fracciones de VWCE, CEMF, SGLD y XEON (el listado de la API no lo dice).
- **Divisas como laboratorio en papel con la IA** (decision 14): sin empezar.
- **Panel de Ploutos:** tiene el mismo hueco de DNS rebinding que se corrigio en Ebisu (S5 de la revision de
  seguridad); se arregla en una sesion de Ploutos, nunca desde aqui. Tambien alli: las comprobaciones de
  Healthchecks se renombraron el 15/10 (`ploutos-...`, con la clave del `.env` en la descripcion; las URL van por UUID
  y no cambian); su documentacion aun usa los nombres antiguos.

## graphify (mapa del proyecto; instalado el 14/10/2026, solo para Ebisu, sin avisos automaticos)

Herramienta (`graphify`, version 0.9.72, en un entorno propio fuera del proyecto; ruta en `CLAUDE.local.md`) que
convierte el proyecto en un grafo consultable en `graphify-out/` (fuera de git). Se usa a mano (opcion A del
propietario): sin hooks.

- Para preguntas sobre el proyecto, `graphify query "<pregunta>"` si existe `graphify-out/graph.json`;
  `graphify path "<A>" "<B>"` para relaciones y `graphify explain "<concepto>"` para un concepto.
- `graphify-out/GRAPH_REPORT.md` solo para una vision general.
- Despues de cambiar codigo, `graphify update .` (solo analiza el codigo, sin coste).
