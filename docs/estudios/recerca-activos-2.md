# Bolsa, bonos y oro desde cero: revision de la literatura y reconstruccion por capas (14/10/2026)

Pedida por el propietario: "repasem i reconstruim l'estrategia com hem fet amb l'ultim intent amb les divises".
Skills usadas: `literature-review` (revision exploratoria), `ml4t-case-study-development` (por que fallaron los
estudios 1 y 2), `ml4t-non-stationarity` (datos de hace 50 anyos). **Nada medido.** Complementa
`docs/estudios/recerca-mejoras.md` (13/10: amplitud y pesos por volatilidad) y `docs/estudios/datos-antes-2000.md`.

Condiciones fijas: 250 €, sin apalancamiento (decision 5), decisiones mensuales, 1971-2026 por tipos de mercado y
tambien 1990-2026 (decision 14), contra la bolsa mantenida, impuestos espanyoles (19-23 % por venta con ganancia).

## 1. Pregunta y criterios

¿Que tiene evidencia de (a) seguir funcionando despues de publicarse, (b) proteger en los tipos de mercado malos
(bolsa a la baja, inflacion alta) y (c) sobrevivir a impuestos y costes de un particular?
Dentro: revistas, documentos de trabajo, gestoras con metodo. Se marca el nivel. Varias fuentes leidas solo por
resumenes de terceros (se dice).

## 2. Evidencia

| Estudio | Tipo | Datos | Hallazgo | Limites |
|---|---|---|---|---|
| Hurst, Ooi y Pedersen (2017), *JPM* | Articulo (gestora AQR) | 67 mercados, 1880-2016 | Tendencia con rendimiento medio positivo en **todas las decadas**; bien en 8 de las 10 peores caidas de una cartera 60/40; caidas propias de hasta ~25 % en giros bruscos | Simulado, con apalancamiento y cortos (no es lo nuestro); leido por resumenes |
| Zakamulin (2015-2017), SSRN 2677212 | Documento + libro | Bolsa EE. UU., 1860-2014 | Las medias moviles ganan en Sharpe a mantener, **sobre todo en las bajadas**; muchas senyales falsas; **sin superioridad estadistica despues de 1932**; el plazo optimo cambia con el tiempo | Leido por resumenes |
| Faber (2007; revision 2018, *JPM*) | Articulo | 5-13 clases, desde 1973 | Fuera de muestra (2008-2017) bien en la crisis; **por detras de la bolsa 6 de 8 anyos despues** | Las cifras, por resumenes |
| Neville, Draaisma, Funnell, Harvey y Van Hemert (2021), *JPM* | Articulo (premiado) | EE. UU., R. Unido, Japon, 1926-2020 | En los 8 episodios de inflacion alta, bolsa y bonos pierden en real; **la tendencia es la proteccion activa mas fiable** (positiva en todos); materias primas, bien pero muy variables | Sin cifra de oro en lo leido |
| Harvey y otros (2018), *JPM* | Articulo | 60+ activos, desde 1926 | Escalar por volatilidad **reduce las colas** en todas las clases; mejora el Sharpe solo en bolsa y credito | - |
| Cederburg, O'Doherty, Wang y Yan (2020), *JFE* | Articulo | 103 estrategias de bolsa | Hecho en tiempo real, el control de volatilidad **no mejora** de forma fiable (peor en 72 de 103) | Factores de bolsa, no la bolsa entera en largo |
| Molenaar y otros (2023); Campbell, Sunderam y Viceira (2017) | Articulo / documento | EE. UU. desde 1875 | Bolsa y bonos van **juntos** con inflacion alta (anyos 70, 2022) y **opuestos** con inflacion baja (2000-2021): los bonos no protegen siempre | Leido por resumenes |
| Erb y Harvey (2013), NBER 18706 | Documento | Oro, siglos | El oro protege de la inflacion solo a plazo de **siglos**; en plazos practicos, no es fiable; precio real alto -> rendimientos bajos despues | Valoracion de 2012 |
| Research Affiliates, "Tactical and Tax Aware GTAA" | Gestora | Multiactivo sin apalancamiento | Los impuestos pueden comerse la ventaja; con seleccion de lotes y compensar perdidas se recupera **la mayor parte** | Solo resumen |
| Practicantes (MyPlanIQ, Newfound) | Comentarios | - | Coste fiscal de la rotacion tactica, **~1-2 puntos al anyo** | Regla de pulgar |

## 3. Sintesis

1. **Seguir la tendencia protege en las bajadas y en la inflacion (confianza alta).** Es el hallazgo mas repetido en
   un siglo de datos. Concuerda con lo que vimos: H1 caia un 11-17 % frente al 53 %.
2. **Pero no gana a la bolsa en las subidas, y su ventaja se ha debilitado (confianza alta).** Zakamulin: sin
   superioridad estadistica desde 1932 en la bolsa de EE. UU. sola; Faber: por detras 6 de 8 anyos tras 2009. Su
   valor esta en **perder menos**, no en ganar mas: encaja con la regla de la decision 14 ("casi igual con menos
   caida"), no con "ganar mas".
3. **Los bonos no son una proteccion fija (confianza media-alta).** Con inflacion alta caen con la bolsa. La tendencia
   lo resuelve sola (sale de lo que baja), sin reglas de regimen aparte.
4. **El control de volatilidad: reduce colas, pero no sube el rendimiento de forma fiable (evidencia dividida).**
   Sin apalancamiento solo puede reducir peso: sirve de capa de proteccion, no de motor.
5. **El oro: diversifica a veces, no protege de forma fiable (confianza media).** Vale como una pieza mas con su propia
   tendencia, no como seguro.
6. **Los impuestos son el enemigo silencioso (confianza media).** 1-2 puntos al anyo pueden ser toda la ventaja. Hace
   falta una capa fiscal: fondos con traspaso (sin impuesto hasta el final, sin oro, no automatico) o ETF con reglas
   que eviten vender con ganancia sin motivo.
7. **Pocos activos = poca ventaja (de recerca-mejoras).** Con 3 piezas hay pocas tendencias independientes.

## 4. Reconstruccion por capas (como en el estudio 3 de divisas)

| Capa | Que hace | Evidencia | Riesgo principal |
|---|---|---|---|
| 1. Senyal | Tendencia por activo, varios plazos (H1, intacta) | Alta (seccion 2) | Senyales falsas en mercados sin direccion |
| 2. Tamanyo | Reduce el peso de lo que se mueve mucho; nunca por encima de 1x | Dividida | Que solo reste rendimiento |
| 3. Fiscal | No vender por cambios pequenyos; compensar perdidas; elegir lotes | Media | Complicar sin ganar |
| 4. Proteccion | Reglas duras: 1x, sin margen, limites por activo | - (seguridad) | - |
| 5. IA | Explica y puede frenar compras (decision 8); solo se prueba hacia delante | No probable con el pasado | Que no aporte |

Lo que se puede medir con la historia: capas 1-3. La 5 va al laboratorio en papel.

## 5. Que hace en cada tipo de mercado (lo esperado por la literatura, no medido)

| Escenario | Ejemplos | Que deberia hacer | Que capa | Debilidad conocida |
|---|---|---|---|---|
| Caida lenta y larga | 1973-74, 2000-02, 2008 | Sale a tiempo: **su punto fuerte** | 1 | - |
| Inflacion alta | 1973-81, 2022 | Sale de bolsa y bonos si caen; oro si sube | 1 | Si todo cae a la vez, solo queda el monetario |
| Caida rapida y rebote | 1987, 2020 | Sale tarde y vuelve tarde: **pierde dos veces** | 2 reduce algo | **La peor**; nada lo evita del todo |
| Mercado sin direccion | 2011, 2015-16, 2018 | Entra y sale: costes e impuestos | 3 | Senyales falsas |
| Subida larga | 1982-99, 2015-26 | Dentro, pero entra tarde: algo por detras | - | Se queda atras (permitido hasta 5 puntos) |
| El euro sube contra el dolar | 2002-08 | Los activos en dolares pierden en euros | Activos en euros o cubiertos | Riesgo de divisa (sin decidir) |

## 6. Huecos

- **Datos de la bolsa mundial antes de 1990:** MSCI World existe desde 1969 (simulado antes de 1986), pero no se ha
  comprobado una descarga gratuita. Sin ella, la bolsa seria la de EE. UU. (Kenneth French, desde 1926).
- **El oro antes de 2000:** solo medias mensuales gratuitas (sesgo a favor de la tendencia).
- **Ninguna fuente** prueba estas estrategias con la fiscalidad espanyola: lo medira nuestro simulador.
- Muchas cifras, por resumenes de terceros.

## Referencias (leidas el 14/10/2026)

- Hurst, Ooi y Pedersen, [A Century of Evidence on Trend-Following Investing](https://fairmodel.econ.yale.edu/ec439/hurst.pdf); resumen de [Cambridge Associates](https://publishedresearch.cambridgeassociates.com/investment-publications-highlights-first-quarter-2018/).
- Zakamulin, [A Comprehensive Look at the Empirical Performance of Moving Average Trading Strategies (SSRN 2677212)](https://papers.ssrn.com/abstract=2677212); resumenes de [CXO Advisory](https://www.cxoadvisory.com/technical-trading/market-timing-with-moving-averages-over-the-very-long-run) y [Alpha Architect](https://alphaarchitect.com/2016/04/the-moving-average-research-king-valeriy-zakamulin/).
- Faber, revision a 10 anyos: [Swedroe en etf.com](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist), [Advisor Perspectives](https://www.advisorperspectives.com/articles/2014/10/28/how-moving-average-strategies-can-really-work), [Quantpedia](https://quantpedia.com/strategies/asset-class-trend-following).
- Neville y otros, [The Best Strategies for Inflationary Times (SSRN 3813202)](https://www.evidenceinvestor.com/wp-content/uploads/2021/12/SSRN-id3813202.pdf); [Man Institute](https://www.man.com/maninstitute/best-strategies-for-inflationary-times); [Alpha Architect](https://alphaarchitect.com/the-best-strategies-for-dealing-with-inflation-factors-and-trend-following/).
- Harvey y otros, [The Impact of Volatility Targeting (SSRN 3175538)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175538); [Alpha Architect](https://alphaarchitect.com/?p=47376).
- Cederburg y otros, [On the Performance of Volatility-Managed Portfolios (JFE 2020)](https://www.lehigh.edu/~xuy219/research/COWY.pdf); [Alpha Architect](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/).
- Correlacion bolsa-bonos: [Alpha Architect sobre Molenaar y otros](https://alphaarchitect.com/?p=87579), [Franklin Templeton](https://www.franklintempleton.com/articles/2023/brandywine-global/deconstructing-the-dynamic-duo-of-stocks-and-bonds).
- Erb y Harvey, [The Golden Dilemma (NBER 18706)](https://causalclaims.trfetzer.com/paper/w18706.html); [Advisor Perspectives](https://www.advisorperspectives.com/newsletters12/The_False_Promise_of_Gold_as_an_Inflation_Hedge.php).
- Impuestos: [Research Affiliates, Tactical and Tax Aware GTAA](https://www.researchaffiliates.com/content/dam/ra/publications/pdf/713-tactical-and-tax-aware-gtaa.pdf), [Newfound](https://blog.thinknewfound.com/tag/taxes/), [MyPlanIQ](https://www.myplaniq.com/invest/september-24-2012-tax-efficient-investing/).
- MSCI World desde 1969: [Wikipedia](https://en.wikipedia.org/wiki/MSCI_World), [investingintheweb](https://investingintheweb.com/blog/msci-world-index-historical-data/).

## Registro de busquedas (14/10/2026)

| Consulta | Resultado util |
|---|---|
| Zakamulin market timing moving averages out-of-sample 1860-2015 | SSRN 2677212, CXO, Alpha Architect |
| Neville ... Best Strategies for Inflationary Times | JPM 2021, Man, Alpha Architect |
| Harvey ... Impact of Volatility Targeting | JPM 2018, resumenes |
| stock bond correlation inflation regime | Molenaar 2023 (resumen), Franklin Templeton |
| after-tax tactical asset allocation | Research Affiliates, Newfound, MyPlanIQ |
| Cederburg ... volatility-managed portfolios | JFE 2020 |
| Erb Harvey Golden Dilemma | NBER 18706 (resumenes) |
| Faber 10-month out-of-sample 2010s | Swedroe, Advisor Perspectives |
| Hurst Ooi Pedersen century | JPM 2017 (resumenes, copia en Yale) |
| MSCI World history 1969 free | Sin descarga gratuita comprobada |
