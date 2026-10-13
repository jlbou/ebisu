# Investigacion: por que pierde comprar en el minimo de ayer y como tratar cada escenario (13/10/2026)

Pedida por el propietario tras H2 (no pasa en 2003-2014 ni en 2015-2026) y las comprobaciones informativas
(`docs/estudios/h2-horas.md` y las del objetivo sin stop). **Solo lectura de fuentes y de lo ya medido; no se ha probado
nada nuevo.** Se leyeron resumenes y fichas, no los textos completos: se dice el nivel de cada fuente.

## 1. Lo que ya sabemos de nuestros datos (7 pares principales, 2003-2026)

- Comprar en el minimo de ayer gana el 45-50 % de las veces; cuando pierde, pierde mas de lo que gana cuando gana.
- Sin stop y esperando a que vuelva: vuelve el 96-100 % de las veces, pero el 1-4 % no vuelve nunca o tarda anyos,
  con caidas del 35-50 % (EUR/USD 2008, GBP/USD 2007, USD/CHF 2003, AUD/USD 2011). Con objetivo en la mitad del rango
  de ayer, el saldo esperado queda cerca de cero.
- Es el perfil "sube por la escalera, baja en ascensor": muchas ganancias pequenyas y pocas perdidas enormes.

## 2. Lo que dice la literatura

| Tema | Evidencia | Nivel | Para Ebisu |
|---|---|---|---|
| Reversion a corto plazo en divisas | Existe y es estable (Krohn, Mueller y Whelan, J. of Finance 2024: el dolar sube antes de los "fixings" y baja despues, en los 9 pares mas operados durante 21 anyos, por la cobertura de los bancos). Neely y Weller: las reglas intradia no ganan tras costes reales | Academico | Hay reversion, pero en horas concretas y pequenya; el rango del dia anterior no la captura |
| Las perdidas grandes vienen de saltos | Los saltos se concentran en noticias programadas (empleo de EE. UU., decisiones de la Fed) y en crisis (rescates, quiebras); en recesion son mayores | Academico | Escenario identificable de antemano: el calendario es publico |
| Asimetria de las divisas | Las divisas de tipos altos suben despacio y caen de golpe, sobre todo cuando baja el apetito por el riesgo (Brunnermeier, Nagel y Pedersen) | Academico | Escenario identificable: caidas de varios pares a la vez y volatilidad alta |
| Stops | Con precios sin memoria, un stop siempre resta; con reversion, resta (te saca antes del rebote); solo suma cuando hay tendencia (Kaminski y Lo, 2014) | Academico | No basta un stop fijo: hay que distinguir rango de tendencia |
| Detectar rango o tendencia | Indicadores (Hurst, ADX, autocorrelacion) con umbrales tipicos; votacion y "no operar si no esta claro". Sin pruebas publicadas serias en divisas | Practicantes | Idea razonable, sin evidencia: se tendria que probar |
| Que el bot "aprenda" que operaciones evitar (meta-etiquetado) | Una regla simple decide la direccion y un segundo modelo aprende, con datos del momento de la senyal, que senyales suelen perder. Riesgo alto de sobreajuste y de mezclar datos de prueba; resultados mixtos | Libro de Lopez de Prado + practicantes | Es exactamente "que el bot sepa leer los casos"; exige datos limpios separados |

## 3. Escenarios en que una compra en el minimo pierde (para clasificar, no medido)

1. **Noticia programada** (Fed, BCE, empleo de EE. UU.) el mismo dia o el siguiente.
2. **Tendencia fuerte en contra** (el par lleva semanas o meses bajando).
3. **Volatilidad disparada** (rango del dia muy por encima de lo normal).
4. **Huida del riesgo** (varios pares caen a la vez contra el yen, el franco o el dolar).
5. **Rotura de un minimo mayor** (no solo el de ayer, sino el de varias semanas).
6. **Cambio de regimen** (un banco central cambia de politica; Brexit; fin del suelo del franco): no se ve venir con
   precios; como mucho, la IA leyendo noticias, que no se puede probar con la historia.

## 4. El problema de los datos limpios

Los 7 pares principales de 2003-2026 ya se han visto enteros. Cualquier tratamiento de escenarios disenyado con ellos
se tiene que probar en datos que nadie haya mirado: **otros pares de Dukascopy** (cruces y divisas menores, sin
comprobar cuales hay ni desde cuando) y, despues, papel hacia adelante. Los cruces son combinaciones de los pares
principales (EUR/JPY = EUR/USD x USD/JPY), asi que solo son **parcialmente** limpios. Y el riesgo de este tipo de
estrategia esta en los dias raros: unos meses de papel no lo pueden confirmar.

## Fuentes (leidas el 13/10/2026)

- Reversion y "fixings": [Krohn, Mueller y Whelan (Bank of Canada SWP 2021-48)](https://www.bankofcanada.ca/wp-content/uploads/2021/10/swp2021-48.pdf);
  reglas intradia tras costes: [Neely y Weller (1999)](https://text.www2.warwick.ac.uk/fac/soc/wbs/subjects/finance/research/wpaperseries/1999/99-89.pdf);
  reversion en EUR/USD de 1 minuto: [Folia Oeconomica Stetinensia (2015)](https://reference-global.com/article/10.1515/foli-2015-0014).
- Saltos y noticias: [Wang et al., crisis de EE. UU. y Europa](https://international.vlex.com/vid/macroeconomic-news-public-communications-855589516),
  [tesis de Brock University](https://brocku.scholaris.ca/items/d3bea987-4676-43d1-a875-f02b204e9a7a),
  [El Ouadghiri y Uctum (2016)](https://hal-univ-paris10.archives-ouvertes.fr/hal-01386027).
- Asimetria: [Brunnermeier, Nagel y Pedersen, Carry Trades and Currency Crashes](https://www.nber.org/papers/w14473),
  [Daniel, Hodrick y Lu](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf).
- Stops: [Kaminski y Lo, When do stop-loss rules stop losses?](https://dspace.mit.edu/handle/1721.1/114876).
- Rango o tendencia: [MQL5, RegimeRouter](https://www.mql5.com/en/code/77535), [LuxAlgo, Hurst](https://www.luxalgo.com/library/concept/hurst-exponent.md).
- Meta-etiquetado: [Wikipedia](https://en.wikipedia.org/wiki/Meta-Labeling),
  [Hudson & Thames](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy/),
  [QuantConnect, no es una bala de plata](https://www.quantconnect.com/forum/discussion/14706/why-meta-labeling-is-not-a-silver-bullet/).
