# Estudio 2: veredicto de la RESERVA (2015-01-01 a 2026-09-30)

Generado por `estudios/estudio2/medir2.py` con el criterio de `docs/diseno-estudio-2.md`. Una sola vez,
sin retoques. Cada candidata con su referencia (E2: MSCI World en euros; H1-F: la del estudio 1).

| Candidata | TAE neta | Caida max. | Sharpe | Confianza (>= 0,95) | Operaciones | Referencia: TAE / caida | Pasa |
|---|---|---|---|---|---|---|---|
| E2 | 1.59% | 8.9% | 0.30 | 0.851 | 693 | 10.54% / 33.6% | no |
| H1-F | 2.64% | 14.7% | 0.43 | 0.928 | 167 | 10.22% / 34.2% | no |

Condiciones:

- **E2**: 1. gana o casi iguala con menos caida: NO; 2. no pierde: si; 3. exceso sobre el monetario con confianza >= 0,95: NO
- **H1-F**: 1. gana o casi iguala con menos caida: NO; 2. no pierde: si; 3. exceso sobre el monetario con confianza >= 0,95: NO

**Veredicto: NO PASA NINGUNA: Ebisu se cierra con el indexado mantenido.**

Informacion que no decide (doble exposicion, antes de impuestos):

- E2: TAE 2.54%, caida 19.2%
- H1-F: TAE 5.31%, caida 27.9%

---

Nota anyadida despues (no cambia ningun numero): la frase "Ebisu se cierra" la escribe el programa, que es anterior a
la decision 12 (`docs/decisiones/12-si-no-pasa.md`, subida a git antes de medir, commit d3e0f7b). Se aplica esa
decision: se permite un estudio 3 con datos anteriores al 2000, y Ebisu como bot del indexado como red de seguridad.
