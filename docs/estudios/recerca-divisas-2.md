# Revision de la literatura: tres estrategias de divisas con evidencia (14/10/2026)

Generada con la skill `literature-review`. Tipo: **revision exploratoria (scoping)**, no sistematica: busqueda en la web
(motores generales, SSRN, NBER, arXiv, repositorios universitarios), lectura de resumenes y, en el caso del "fixing",
del articulo completo. Ventana: publicaciones 1999-2026. **Nada medido.**

## Pregunta

Para un particular con 250 €, CFD a ~4x, una posicion abierta, minimo de 1.000 unidades, costes de Dukascopy y la
fiscalidad espanyola: ¿cual de estas tres estrategias tiene evidencia que (a) siga en pie despues de publicarse,
(b) sobreviva a los costes y (c) encaje con esas condiciones?

1. Momento o tendencia en divisas (time-series y cross-sectional).
2. Carry (cobrar la diferencia de tipos) y su riesgo de caidas.
3. Reversion alrededor de los "fixings" (Krohn, Mueller y Whelan).

## Criterios

- Dentro: estudios academicos (revistas, documentos de trabajo de bancos centrales y universidades) y datos de
  gestoras con metodo explicado. Fuera: blogs sin datos, foros, promociones de brokers.
- Se marca el nivel de cada fuente: articulo revisado, documento de trabajo, preprint o comentario.

## Evidencia

| Estudio | Tipo | Datos | Hallazgo | Limites |
|---|---|---|---|---|
| Menkhoff, Sarno, Schmeling y Schrimpf (2012), *J. of Financial Economics* | Articulo | 48 divisas, 1976-2010 | Momento entre divisas: hasta un 10 % al anyo entre ganadoras y perdedoras; los costes se comen parte; "limites al arbitraje muy efectivos" | Se concentra en divisas poco liquidas; en las G10 apenas se ve (comentario de Cass) |
| Moskowitz, Ooi y Pedersen (2012), *J. of Financial Economics* | Articulo | 58 futuros, 1985-2009 | Tendencia (time-series) rentable en todas las clases, divisas incluidas | Muestra anterior a la publicacion |
| Hsu, Taylor y Wang (2016), *J. of International Economics* | Articulo | 30 divisas, ~45 anyos, 21.000 reglas | Hay reglas tecnicas rentables, pero **variables en el tiempo** y en mercados inmaduros | Solo leido el resumen |
| Eisler y otros (2026), arXiv 2607.01550 | **Preprint** | ~100 futuros, 1995-2025 | La tendencia a corto plazo **dejo de funcionar hacia 2009** en los contratos de "tick" pequenyo; en **divisas y bolsa, practicamente desaparecida** | Preprint reciente; leido por resumenes |
| Menkhoff, Sarno, Schmeling y Schrimpf (2012), *J. of Finance* | Articulo | Carteras de carry | El carry pierde cuando sube la volatilidad mundial de las divisas (explica >90 % de sus rendimientos) | - |
| Brunnermeier, Nagel y Pedersen (2009), *NBER Macro Annual* | Articulo | Carry G10 | Las divisas de tipos altos "suben por la escalera y bajan en ascensor": caidas bruscas | Solo leido el titulo y citas |
| Jurek (comentario a carry neutral a caidas) | Documento | Carry cubierto | Quitando el riesgo de caida, el rendimiento del carry **no se distingue de cero** | - |
| Mackenzie (2023), comentario | Gestora | Indice Goldman Sachs Carry | ~10,8 % al anyo en 2000-2007; **languidece tras 2008** | Comentario, sin tabla completa |
| **Krohn, Mueller y Whelan** (2021 documento del Banco de Canada; 2024 *J. of Finance*) | Articulo (leido entero) | 9 divisas contra el dolar, 1999-2019, datos de 5 minutos | El dolar sube antes de los fixings de Tokio, BCE y Londres y baja despues: **~2,5 puntos basicos por dia y ventana**; en 59 % de los dias sale bien; asimetria positiva (lo contrario del carry) | **Con el diferencial entero, la estrategia pierde**; con la mitad, gana (Sharpe 0,1-1,0). El efecto **baja en 2014-2019** (Tokio: anyos negativos desde 2018; Europa: <5 % en los dos ultimos). Mas fuerte cuando el VIX esta alto |

## Sintesis por tema

1. **Tendencia en divisas (confianza alta en que se ha debilitado).** Funcionaba bien hasta los 90-2000; desde ~2009
   ha desaparecido practicamente en divisas (Eisler y otros; Deutsche Bank ya lo veia en 2007). El momento entre
   divisas necesita muchas posiciones a la vez (compra unas, vende otras): **no cabe con una sola posicion**.
2. **Carry (confianza media).** Paga a la larga, pero con caidas bruscas en las crisis; sin ese riesgo, no queda
   rendimiento. Tras 2008 rindio poco. Para nosotros: los intereses del broker (recargo de ~1,5 % al anyo) se comen
   parte del diferencial, y a ~4x una caida como la de 2008 **no pasaria el liston de riesgo M** (caida < 30 %).
3. **Fixings (confianza alta en el patron; media-baja en que sea explotable).** El patron es real, robusto en 21 anyos,
   en todas las divisas y con datos de operaciones reales, con una explicacion economica (los bancos se cubren antes del
   fixing). Pero es diminuto (~2,5 pb por ventana) y los propios autores dicen que "no es obvio que lo pueda aprovechar
   el operador medio"; ademas se ha ido reduciendo.

## Encaje con las condiciones de Ebisu

| | Tendencia | Carry | Fixings |
|---|---|---|---|
| Evidencia despues de publicarse | Desaparecida en divisas | Debil tras 2008 | Reduciendose; **2020-2026 sin estudiar** |
| Costes | Pocos (mensual) | Intereses del broker en contra | **Decisivos**: el margen es de ~2,5 pb |
| Una posicion, 1.000 unidades | La de una sola serie, si; la de varias divisas, no | Si | Si (una posicion en cada ventana) |
| Riesgo a ~4x | Medio | **Alto (crisis)** | Bajo (posiciones de horas, sin noches ni fines de semana; asimetria positiva) |
| Prueba limpia posible | Los 25 pares nuevos | Los 25 pares nuevos | **2020-2026 (fuera de la muestra de los autores)** y pares con dolar no tratados (USD/NOK, USD/SEK...) |
| Datos que tenemos | Si | Si (tipos del BIS) | Velas de 1 hora: aproximan las ventanas (el fixing del BCE es a las 8:15 de Nueva York, entre dos velas) |

## Huecos y limites

- No se ha encontrado ningun estudio de los fixings con costes de un broker minorista ni despues de 2019.
- Nuestros costes en Dukascopy (comision de ~0,35 pb por lado mas el diferencial real, en horas liquidas ~0,1-0,5 pb
  en EUR/USD) parecen **menores** que los diferenciales "indicativos" del articulo, pero sin comprobar en las horas de
  cada ventana.
- Varias fuentes se leyeron solo por resumen (marcado en la tabla).

## Referencias

- Krohn, Mueller y Whelan, [Foreign Exchange Fixings and Returns Around the Clock, Bank of Canada SWP 2021-48](https://www.bankofcanada.ca/wp-content/uploads/2021/10/swp2021-48.pdf) (version en *J. of Finance* 2024).
- Menkhoff, Sarno, Schmeling y Schrimpf, [Currency momentum strategies (JFE 2012)](https://openaccess.city.ac.uk/id/eprint/3296/) y [Carry trades and global FX volatility (JF 2012)](https://openaccess.city.ac.uk/id/eprint/3391/).
- Moskowitz, Ooi y Pedersen, [Time Series Momentum](https://papers.ssrn.com/abstract=2089463).
- Hsu, Taylor y Wang, [Technical trading: is it still beating the foreign exchange market? (JIE 2016)](https://profiles.wustl.edu/en/publications/technical-trading-is-it-still-beating-the-foreign-exchange-market/).
- Eisler y otros, [Is Trend Still Your Friend? (arXiv 2607.01550, preprint)](https://arxiv.org/abs/2607.01550); resumen de [Quantpedia](https://quantpedia.com/is-trend-still-your-friend-a-microstructural-account-of-the-demise-of-short-term-trend-following/).
- Brunnermeier, Nagel y Pedersen, [Carry Trades and Currency Crashes (NBER)](https://www.nber.org/papers/w14473); Jurek, [Crash-neutral currency carry trades](https://www.johnhcochrane.com/s/jurek_currency.pdf).
- Mackenzie Investments, [comentario de junio de 2023](https://www.mackenzieinvestments.com/content/dam/mackenzie/en/insights/jules-boudreau-monthly-commentary-june-2023-en.pdf); Deutsche Bank, [FX momentum (2007)](https://my.liuc.it/MatSup/2006/F86032/DeutscheBank_MomentumInvesting_070329.pdf).

## Registro de busquedas (14/10/2026)

| Fuente | Consulta | Resultado util |
|---|---|---|
| Web | Menkhoff Sarno Schmeling Schrimpf currency momentum transaction costs | JFE 2012 y comentario de Cass |
| Web | time series momentum currencies after 2012 decline | AQR, Eisler y otros 2026, Deutsche Bank 2007 |
| Web | carry trade after 2008 crash risk Menkhoff Lustig Roussanov Verdelhan | JF 2012, NBER, Jurek |
| Web | Hsu Taylor Wang technical trading still beating FX | JIE 2016 |
| Web | Krohn Mueller Whelan fixing reversal magnitude costs | Documento del Banco de Canada (leido entero) |
| Web | Kurth/Eisler Bouchaud trend tick size | arXiv 2607.01550 |
| Web | G10 carry index 2008-2024 performance | Mackenzie, UBS, MUFG (fragmentos) |
