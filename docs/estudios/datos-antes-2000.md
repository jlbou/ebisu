# Bolsa, bonos y oro desde cero: datos disponibles y anyos necesarios (14/10/2026)

Paso A del replanteamiento (el propietario no quiere el indexado: vuelve a bolsa, bonos y oro "bien hecho"). Solo se
comprueba **que datos existen y desde cuando**; no se ha calculado ninguna estrategia ni mirado ningun rendimiento.

## Por que fallaron los estudios 1 y 2 (revision con la skill `ml4t-case-study-development`)

1. **Pocos datos para distinguir habilidad de suerte.** H1 cumplio las condiciones 1 y 2 en 2001-2014 (caidas del
   11-17 % frente al 52,8 %), pero no el liston contra la suerte (H1-F: 0,942 con la varianza de H1; hacia falta 0,95).
   Nunca se calculo antes si 13,5 anyos con ~12 decisiones al anyo bastaban. No bastaban (tabla de abajo).
2. **Un solo periodo decidio.** La reserva 2015-2026 fue una decada muy alcista para la bolsa, donde lo que protege
   siempre se queda atras.
3. El metodo (criterio antes, reserva una vez) era correcto: lo que fallo fue plantear una prueba casi imposible de pasar.

## Anyos necesarios para pasar el liston contra la suerte (aproximado)

Sharpe deflactado >= 0,95 con N variantes probadas, decisiones mensuales, rendimientos normales (sin asimetria ni colas):
anyos >= ((1,645 + Z(N)) / S)², con S el Sharpe anual real sobre el monetario y Z(N) el maximo esperado por suerte.

| Sharpe real (S) | N = 10 | N = 30 | N = 50 |
|---|---|---|---|
| 0,3 | 115 | 154 | 171 |
| 0,5 | 41 | 55 | 62 |
| 0,7 | 21 | 28 | 31 |
| 1,0 | 10 | 14 | 15 |

Seguir la tendencia en varios activos sin apalancamiento suele dar S de 0,4-0,7 en la literatura: hacen falta
**~20-60 anyos** de datos. Con 13,5 solo pasaria algo con S >= 1, muy raro.

## Datos gratuitos comprobados (14/10/2026)

| Activo | Serie | Desde | Frecuencia | Comprobado |
|---|---|---|---|---|
| Bolsa EE. UU. (con dividendos) y letras del Tesoro | [Kenneth French, factores Fama-French](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) (CRSP) | 07/1926 | mensual y diaria | si (descargado, cabecera) |
| Bolsa EE. UU., dividendos, IPC, tipo largo | [Shiller, ie_data.xls](http://www.econ.yale.edu/~shiller/data.htm) | 1871 | mensual | existe (HTTP 200); sin abrir |
| Bono EE. UU. a 10 anyos (rentabilidad) | FRED GS10 / DGS10 | 04/1953 / 01/1962 | mensual / diaria | si |
| Letras del Tesoro a 3 meses | FRED TB3MS | 01/1934 | mensual | si |
| Bono aleman a 10 anyos | FRED IRLTLT01DEM156N | 05/1956 | mensual | si |
| Marco aleman / dolar (para pasar a euros) | FRED EXGEUS | 01/1971 (hasta 2001) | mensual | si |
| Oro | [Banco Mundial (Pink Sheet)](https://eco3min.fr/en/gold-price-history-dataset/), [DataHub gold-prices](https://datahub.io/core/gold-prices) | 1960 | mensual | sin descargar |

Limites, sin resolver:

- **Oro:** las series gratuitas son **medias del mes**, no cierres; una media suaviza y hace parecer mejor seguir la
  tendencia. Hay que buscar cierres o corregirlo. El oro solo cotiza libre desde ~1968-1971.
- **Bonos:** solo hay rentabilidades, no precios: el rendimiento del bono se calcula a mano (aproximacion conocida).
- **Bolsa europea antes de 1975:** sin fuente gratuita comprobada (los paises de Kenneth French no se pudieron bajar).
- Los tres activos juntos en euros: desde **~1971**. Bolsa y bonos de EE. UU.: desde 1926 (bonos con Shiller) o 1953.

## Lo que queda por decidir

Como se dividen los datos por tipos de mercado (idea del propietario) y que cuenta como ganar, antes de medir nada.
