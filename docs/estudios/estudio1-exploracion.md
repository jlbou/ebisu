# Estudio 1: veredicto de la EXPLORACION (2001-07-01 a 2014-12-31)

Generado por `estudios/estudio1/medir.py` con el criterio de `docs/diseno-estudio-1.md`. Sin retoques.
H2 empieza el 2003-08-04 (cuando hay datos de los siete pares).

| Variante | TAE neta | Caida max. | Sharpe | Deflactado | Operaciones | Referencia: TAE / caida | Pasa |
|---|---|---|---|---|---|---|---|
| H1-M | 3.90% | 12.2% | 0.34 | 0.004 | 282 | 2.98% / 52.8% | no |
| H1-S | 2.72% | 11.0% | 0.16 | 0.001 | 852 | 2.98% / 52.8% | no |
| H1-MB | 4.47% | 16.5% | 0.37 | 0.006 | 104 | 2.98% / 52.8% | no |
| H1-F | 4.88% | 10.9% | 0.70 | 0.096 | 171 | 2.98% / 52.8% | no |
| H2 | -3.94% | 38.7% | -1.54 | 0.000 | 9821 | 7.13% / 52.8% | no |

Condiciones de cada variante:

- **H1-M**: 1. gana o casi iguala con menos caida: si; 2. no pierde: si; 3. no es suerte (deflactado >= 0,95): NO
- **H1-S**: 1. gana o casi iguala con menos caida: si; 2. no pierde: si; 3. no es suerte (deflactado >= 0,95): NO
- **H1-MB**: 1. gana o casi iguala con menos caida: si; 2. no pierde: si; 3. no es suerte (deflactado >= 0,95): NO
- **H1-F**: 1. gana o casi iguala con menos caida: si; 2. no pierde: si; 3. no es suerte (deflactado >= 0,95): NO
- **H2**: 1. gana o casi iguala con menos caida: NO; 2. no pierde: NO; 3. no es suerte (deflactado >= 0,95): NO; H2. IC 90 % por operacion > 0: NO; H2. positiva en >= 5 de 7 pares: NO

**Veredicto: NO PASA NINGUNA: la conclusion es el indexado mantenido; la reserva queda sin tocar.**

Informacion que no decide (doble exposicion, antes de impuestos):

- H1-M: TAE 5.64%, caida 27.0%
- H1-S: TAE 3.16%, caida 28.0%
- H1-MB: TAE 6.71%, caida 32.8%
- H1-F: TAE 9.35%, caida 22.4%

## Solo informacion (calculado despues del veredicto; no lo cambia)

- La varianza de los Sharpe de las 5 variantes incluye H2, muy distinta (Sharpe -1,54): eso sube el liston. Con la
  varianza de solo las 4 variantes de H1 (y N = 5 igual), el deflactado seria: H1-M 0,604; H1-S 0,350; H1-MB 0,654;
  **H1-F 0,942** (tampoco llega a 0,95). Contra 0, sin corregir por el numero de pruebas: H1-F 0,994, H1-MB 0,914,
  H1-M 0,892, H1-S 0,722.
- Las cuatro de H1 cumplen las condiciones 1 y 2 (ganan a la referencia, 2,98 %, con caidas del 11-17 % frente al
  52,8 %): **protegen mucho, como L en Ploutos, pero el resultado no se distingue lo bastante de la suerte** con 13,5
  anyos y ~12 decisiones al anyo.
- H2 pierde: -3,94 % al anyo, y ni por operacion ni por pares tiene ventaja.
