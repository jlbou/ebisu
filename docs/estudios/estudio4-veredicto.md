# Estudio 4: veredicto (1971-2026 y 1990-2026)

Generado por `estudios/estudio4/medir4.py` con el criterio de `docs/plan-estudio-4.md`. Una vez, sin retoques.

| Variante | TAE 1971-2026 | Caida | Sharpe | Deflactado | TAE 1990-2026 | Caida | Pasa |
|---|---|---|---|---|---|---|---|
| Referencia (bolsa mantenida) | 8.50% | 58.2% | 0.36 | - | 9.12% | 58.2% | - |
| H1-M | 5.57% | 14.9% | 0.48 | 0.983 | 4.63% | 13.9% | no |
| H1-F | 6.50% | 18.9% | 0.48 | 0.972 | 5.79% | 14.8% | no |
| H1-M + volatilidad | 5.17% | 13.9% | 0.46 | 0.966 | 4.49% | 12.8% | no |
| H1-M + fiscal | 5.94% | 23.5% | 0.48 | 0.982 | 4.98% | 14.3% | no |
| H1-M + modelo | 5.79% | 14.4% | 0.48 | 0.982 | 4.63% | 13.9% | no |

Condiciones:

- **H1-M**: 1. 1971-2026: NO; 2. 1990-2026: NO; 3. tipos de mercado: NO; 4. no es suerte (deflactado >= 0,95): si
- **H1-F**: 1. 1971-2026: NO; 2. 1990-2026: NO; 3. tipos de mercado: NO; 4. no es suerte (deflactado >= 0,95): si
- **H1-M + volatilidad**: 1. 1971-2026: NO; 2. 1990-2026: NO; 3. tipos de mercado: NO; 4. no es suerte (deflactado >= 0,95): si
- **H1-M + fiscal**: 1. 1971-2026: NO; 2. 1990-2026: NO; 3. tipos de mercado: NO; 4. no es suerte (deflactado >= 0,95): si
- **H1-M + modelo**: 1. 1971-2026: NO; 2. 1990-2026: NO; 3. tipos de mercado: NO; 4. no es suerte (deflactado >= 0,95): si; 5a. PBO < 0,5: NO; 5b. ninguna variable > 40 %: NO; 5c. mejora el Sharpe de su base: NO

Tipos de mercado (media anual de estrategia - referencia, antes de impuestos):

| Variante | bajada, inflacion alta (8 anyos) | bajada, inflacion baja (8 anyos) | subida, inflacion baja (30 anyos) | subida, inflacion alta (9 anyos) |
|---|---|---|---|---|
| H1-M | +21.8% si | +13.5% si | -11.4% NO | -14.7% NO |
| H1-F | +15.3% si | +14.4% si | -10.5% NO | -14.3% NO |
| H1-M + volatilidad | +20.3% si | +14.2% si | -12.1% NO | -16.9% NO |
| H1-M + fiscal | +21.0% si | +13.4% si | -10.9% NO | -14.2% NO |
| H1-M + modelo | +21.8% si | +13.5% si | -11.4% NO | -14.8% NO |

Modelo: base = H1-M; PBO = 0.77; variable mas importante = 41%.
Liston: N = 10, varianza de los Sharpe mensuales = 0.001497.

**Veredicto: NO PASA NINGUNA.**

Solo informacion (no decide): condicion 1 en 1971-2000 (tramo limpio): H1-M: no; H1-F: no; H1-M + volatilidad: no; H1-M + fiscal: no; H1-M + modelo: no

Anacronismos: ETF antes de 1993, traspasos antes de 2003 y la ley de hoy; tramos en euros de hoy sobre 250 € de 1971; oro de 1999-2000 con medias mensuales; bolsa solo de EE. UU. hasta 1996.

Mas informacion (no decide):

- 1927-1970, H1 sobre la bolsa de EE. UU. (dolares, antes de impuestos): TAE 6.84%, caida 53.4%
- 1927-1970, bolsa de EE. UU. mantenida (dolares, antes de impuestos): TAE 8.73%, caida 84.1%
- 1975-1996, bolsa fuera de EE. UU. media de 10 meses (mensual, dolares, sin el monetario): TAE 10.27%, caida 39.9%
- 1975-1996, bolsa fuera de EE. UU. mantenida (mensual, dolares, sin el monetario): TAE 14.30%, caida 29.4%
