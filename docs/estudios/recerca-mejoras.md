# Investigacion: como mejorar las estrategias y que otras hay (13/10/2026)

Pedida por el propietario tras el veredicto de la exploracion (no paso ninguna: las 4 de H1 cumplen 1 y 2, fallan el
liston contra la suerte; H2 pierde). **Solo lectura de fuentes; no se ha medido nada ni se ha vuelto a mirar la
exploracion.** Muchas fuentes son blogs o backtests de terceros: se dice el nivel de cada una.

## 1. Lo que dice la evidencia, por mejora posible

| Mejora | Evidencia | Nivel | Para Ebisu |
|---|---|---|---|
| **Mas activos (amplitud)** | Faber: pasar de 5 a 13 clases de activo sube el Sharpe de 0,71 a 0,91 con casi la misma volatilidad. Graham y Winton: el Sharpe crece con la raiz del numero de mercados **independientes**, y se satura hacia 40-70. Hurst, Ooi y Pedersen: la tendencia funciona desde 1880 en 4 clases de activo | Academico + gestoras | **La mejor apoyada.** Con 3 piezas, Ebisu tiene muy pocas tendencias independientes |
| **Pesos por volatilidad** (paridad de riesgo: menos peso a lo que mas se mueve) | Harvey et al. (60 activos): mejora el Sharpe en bolsa y credito; en materias primas solo reduce colas. Kim, Tse y Wald: buena parte del "alfa" de la tendencia viene de escalar por volatilidad. Paper de 2026 (acciones, bonos, oro, 2006-2026): el control de volatilidad mejora todas las medidas de riesgo frente a pesos fijos | Academico | **Bien apoyada.** Sin apalancamiento (tope 1x), solo reduce peso, nunca lo aumenta por encima de lo invertido |
| Momento relativo (elegir las mejores N) + filtro absoluto (GTAA 13, momento dual) | Faber GTAA 13: ~8,9 % de media historica, 6,1 % a 10 anyos. Momento dual (GEM): despues del libro de 2014 va por detras de 60/40; el componente absoluto pasa de Sharpe 0,68 a 0,44 | Terceros | **Dudosa:** decae tras publicarse |
| "Canarios" (VAA, DAA de Keller) | Backtests propios espectaculares (>10 %, caidas <15 %); los autores reconocen riesgo de sobreajuste; sin replica independiente | Autores | **No:** demasiado ajustado |
| Revisar mas a menudo | Mas rotacion = mas costes e impuestos; nuestra H1-S (semanal) fue la peor de H1 | Varios + nuestro estudio | **No:** mensual |
| Divisas por rango del dia (H2) | Pierde en nuestro estudio; no hay evidencia seria a favor | - | **Descartada** |

## 2. Sobre el liston contra la suerte (el Sharpe deflactado)

- El deflactado supone que las pruebas son **independientes**. Las 4 variantes de H1 son casi la misma estrategia y H2
  es muy distinta: eso **infla la varianza** de los Sharpe y sube mucho el liston (con solo las 4 de H1, la mejor
  quedaria en 0,942).
- Con pocas decisiones al anyo y rendimientos asimetricos, **el test tiene poca potencia**: un deflactado bajo dice
  "la muestra es corta para confirmarlo", **no** "no hay ventaja". La literatura propone contar las pruebas efectivas
  (descontando las muy correlacionadas) o alargar la historia.
- Nada de esto permite cambiar el liston ya aplicado: el veredicto del estudio 1 queda como esta. Si se usa en un
  estudio nuevo, se fija **antes** de medir.

## 3. Lo que se aprende

1. Ebisu se quedo corto **por pocas piezas**, no por la idea: con 3 activos hay muy pocas tendencias independientes, y
   el exceso sobre el monetario sale pequenyo y depende de dos crisis.
2. Las dos mejoras con mas apoyo son **mas activos poco correlacionados** y **pesos por volatilidad** (sin
   apalancamiento). Las tecnicas de seleccion (momento relativo, canarios) tienen peor historial fuera de muestra.
3. La reserva 2015-2026 **sigue limpia**: es la prueba natural de cualquier propuesta nueva, si se fija antes.

## Fuentes (leidas el 13/10/2026)

- Faber: [A Quantitative Approach to Tactical Asset Allocation, revisado a los 10 anyos](https://allocatortraining.com/wp-content/uploads/2023/06/A-Quantitative-Approach-to-Tactical-Asset-Allocation.pdf),
  [GTAA 13 en PortfolioDB](https://www.portfoliodb.com/portfolios/global-tactical-asset-allocation-13-gtaa-13-meb-faber),
  [Swedroe sobre mas clases de activo](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist).
- Amplitud: [Graham Capital, Market Diversification](https://www.grahamcapital.com/wp-content/uploads/2023/12/Market-Diversification_Graham-Research_August-2017.pdf),
  [Macquarie/Winton](https://www.macquarie.com/au/en/about/company/macquarie-asset-management/financial-advisor/insights/2024/why-diversify-lessons-from-cocoa.html),
  [Hurst, Ooi y Pedersen, A Century of Evidence](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing?aqrPDF=1).
- Volatilidad: [Alpha Architect, volatility targeting](https://alphaarchitect.com/volatility-targeting-improves-risk-adjusted-returns/),
  [Kim, Tse y Wald](https://www.researchgate.net/publication/303846490_Time_series_momentum_and_volatility_scaling),
  [Simple Dynamic Stock/Bond/Gold Portfolios (arXiv 2609.07946)](https://arxiv.org/abs/2609.07946).
- Momento dual: [Quant for Free](https://quant4free.com/analysis/dual-momentum/),
  [TuringTrader](https://www.turingtrader.com/portfolios/antonacci-dual-momentum/),
  [replica fuera de muestra (GitHub)](https://github.com/FranciscoAC-burst/dual-momentum-oos).
- Canarios: [Keller y Keuning, DAA](https://www.researchgate.net/publication/326859452_Breadth_Momentum_and_the_Canary_Universe_Defensive_Asset_Allocation_DAA),
  [Allocate Smartly sobre VAA](https://allocatesmartly.com/vigilant-asset-allocation-dr-wouter-keller-jw-keuning/).
- Liston: [Bailey y Lopez de Prado, Deflated Sharpe Ratio](https://papers.ssrn.com/abstract=2460551),
  [MinervaScore, pruebas correlacionadas (arXiv 2608.23808)](https://arxiv.org/pdf/2608.23808),
  [Sharpe probabilistico y longitud minima](https://portfoliooptimizer.io/blog/the-probabilistic-sharpe-ratio-hypothesis-testing-and-minimum-track-record-length-for-the-difference-of-sharpe-ratios/).
