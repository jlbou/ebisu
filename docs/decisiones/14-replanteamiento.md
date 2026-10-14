# Decision 14: replanteamiento de Ebisu (14/10/2026)

Tras el council (cuatro voces) sobre "repensar el enfoque a fondo" y los estudios 1, 2, H2, el diagnostico del
estudio 3 y la prueba del fixing, todos sin ganadora.

## 14.1 Divisas: laboratorio en papel (opcion A)

- Ebisu funciona en el VPS cada dia con precios reales y opera **solo en papel** en divisas.
- La IA lee noticias y bancos centrales, propone y explica; cada idea se fija por escrito y se cuenta **antes** de
  empezar, y se juzga con un criterio ya decidido.
- Paso a dinero real solo si supera la prueba hacia delante **y** (hay capital para operar sin apalancamiento, ~1.000 €,
  **o** pasa el liston de riesgo M de la decision 13 con los limites reales). Las reglas concretas se fijan antes de
  arrancar el laboratorio.
- Coste: el VPS (ya pagado ~6 meses) y la IA (Claude Pro, ya pagado) **no se cuentan**. Sin verificar: si el bot puede
  usar la suscripcion sin la API de pago.

## 14.2 Los 250 € no van a un indexado

Decision del propietario. Se sustituye la red de seguridad de la decision 12.3 (bot del indexado).

## 14.3 Bolsa, bonos y oro, desde cero y bien hecho

Por que fallaron los estudios 1 y 2 y que datos hay: `docs/estudios/datos-antes-2000.md`. No se ignoran: H1 protegia
mucho en las caidas; el problema fue juzgar con 13,5 anyos (hacian falta ~20-60).

- **Tipos de mercado (opcion A):** regla automatica de dos ejes, bolsa sube o baja e inflacion alta o baja: 4 tipos,
  cada anyo cae en uno. La estrategia tiene que ganar en el total y **no perder mucho en ninguno de los 4**. Los
  umbrales exactos se fijan en el criterio, antes de medir.
- **Periodo (opcion A+):** se juzga con **1971-2026** (55 anyos; los tres activos en euros, oro libre) **y ademas**
  tiene que funcionar en el tramo **1990-2026** (el mas parecido al mercado de hoy). 1926-1970: solo informacion.
- Las reglas de la estrategia solo usan datos pasados recientes (ventanas moviles), nunca estadisticas de toda la
  historia (skill `ml4t-non-stationarity`).
- **Que cuenta como ganar (opcion A):** contra la bolsa mantenida, como la decision 1: gana o casi iguala con
  claramente menos caida, en 1971-2026 y tambien en 1990-2026. El propietario no invierte en el indexado, pero es la
  vara de medir: si no se supera, una cartera simple lo haria mejor sin bot.
- **Numeros (opcion A):** en el total (1971-2026 y 1990-2026), TAE >= la de la bolsa, o TAE >= la de la bolsa - 1 punto
  y caida maxima <= 2/3 de la suya. En los anyos de bolsa a la baja (con inflacion alta o baja), gana a la bolsa en
  media anual; en los de bolsa al alza, se queda como mucho 5 puntos al anyo por detras en media.
- **Como decide el bot (opcion A):** reglas por capas (`docs/estudios/recerca-activos-2.md` 4): H1 intacta como
  senyal, tamanyo por volatilidad y capa fiscal como variantes contadas, reglas duras y la IA en papel.
- **Capa 6, modelo con scikit-learn (opcion A):** opcional, solo entra si mejora. Despues de medir las reglas, un
  modelo que aprende cuando fallan las senyales de tendencia (no predice el mercado), entrenado con los 49 sectores de
  EE. UU. de Kenneth French (mensuales desde 1926). Cuenta como variante; validacion por bloques de tiempo con purga y
  probabilidad de sobreajuste < 0,5. Dependencia nueva: scikit-learn. Sin estudios academicos serios que lo hayan
  hecho con datos mensuales (Goyal, Welch y Zafirov 2024: predecir el mercado con indicadores no funciona).
- **Piezas (opcion A):** las mismas de H1 (bolsa mundial, bonos cubiertos a euros, oro, monetario en euros), para que
  H1 se pruebe intacta en 1971-2000. Datos comprobados (14/10): oro diario en marcos de Frankfurt 1968-1998
  (Bundesbank, BBEX3.D.XAU.DEM.EA.AC.C01, 7.622 dias); bolsa de EE. UU. diaria desde 1926 (Kenneth French); bolsa
  fuera de EE. UU. **solo mensual desde 1975** (Kenneth French, International Indices) y **diaria solo desde 1997**
  (MSCI, gratis desde esa fecha). **Hueco (opcion A):** la pieza de bolsa es la de EE. UU. sola hasta 1996 y la
  mundial (60 % EE. UU. + 40 % resto, MSCI) desde 1997; H1 queda intacta. Solo informacion: la bolsa fuera de EE. UU.
  mensual 1975-1996.
- **Tipos de mercado, umbrales (opcion A):** por anyos naturales. Bolsa a la baja: el anyo en que la referencia (bolsa
  mantenida, en euros) pierde. Inflacion alta: IPC de EE. UU. (FRED CPIAUCSL, diciembre sobre diciembre) > 4 %
  (17 anyos en 1971-2025), porque las piezas son de EE. UU. y la relacion bolsa-bonos depende de su inflacion.
- **Variantes (opcion A):** 5 nuevas (H1-M, H1-F, H1-M + volatilidad, H1-M + fiscal, la mejor + modelo); con las
  5 del estudio 1 y 2 de bolsa, bonos y oro, **N = 10**. Plan completo: `docs/plan-estudio-4.md`.
