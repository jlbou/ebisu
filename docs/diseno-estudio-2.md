# Diseno del estudio 2: criterio fijado ANTES de medir (BORRADOR desde el 13/10/2026)

**Estado: BORRADOR, se aprueba por partes. No se ha medido nada.** Viene de `docs/estudios/estudio1-exploracion.md`
(no paso ninguna) y de `docs/estudios/recerca-mejoras.md` (que mejoras tienen evidencia).

## 0. La idea y las reglas

- **Una sola estrategia nueva, decidida con la literatura y no con los resultados del estudio 1:** seguir la tendencia
  con **mas activos poco correlacionados** y **pesos segun el riesgo**, mensual y sin apalancamiento.
- **Se prueba UNA vez, directamente en la reserva** (2015-2026, que nadie ha mirado). Al ser una sola prueba, no hay
  correccion por muchas variantes.
- Nada se retoca despues de ver el resultado. Si no pasa, Ebisu se cierra con el indexado mantenido.

## 1. Los 9 activos (aprobado por el propietario, 13/10/2026)

El propietario eligio 9 (frente a 5 o 13: ver la recerca). Cada uno con su ETF en euros (vehiculo) y la serie de
precios que se usa para el estudio (historia desde 2013 como mucho, para calentar las medias de 200 dias en 2014).

| # | Activo | ETF (vehiculo) | ISIN | Serie del estudio (Yahoo) |
|---|---|---|---|---|
| 1 | Bolsa EE. UU. | iShares Core S&P 500 (Acc) | IE00B5BMR087 | SXR8.DE (2010) |
| 2 | Bolsa Europa | iShares Core MSCI Europe (Acc) | IE00B4K48X80 | SMEA.MI (2010) |
| 3 | Bolsa emergente | iShares MSCI EM (Acc) | IE00B4L5YC18 | EUNM.DE (2009) |
| 4 | Bonos del Estado de la zona euro | iShares Core EUR Govt Bond | IE00B4WXJJ64 | EUNH.DE (2009) |
| 5 | Bonos corporativos en euros | iShares Core EUR Corp Bond | IE00B3F81R35 | EUN5.DE (2009) |
| 6 | Bonos del Estado de EE. UU. 7-10 anyos (sin cubrir el dolar) | iShares USD Treasury Bond 7-10yr | IE00B1FZS798 | IUSM.DE (2009) |
| 7 | Oro | Invesco Physical Gold (Milan) | IE00B579F325 | 4GLD.DE, Xetra-Gold (2009) |
| 8 | Materias primas | WisdomTree Broad Commodities | GB00B15KY989 | AIGC.MI (2008) |
| 9 | Inmobiliario mundial | iShares Developed Markets Property Yield | IE00B1FZS350 | IQQ6.DE (2008) |

- El lugar 6 iba a ser bonos mundiales cubiertos (EUNA), pero su ETF solo existe desde 2017: el propietario eligio
  los del Estado de EE. UU. (opcion A, 13/10), que suelen ir al reves de la bolsa en las crisis.
- Los ISIN se comprueban en Trading 212 (busqueda por ISIN en la app) antes de aprobar el criterio. Las fechas son las
  de Yahoo, solo fechas (no se ha mirado ningun rendimiento).
- Las series de Yahoo se contrastan con una segunda fuente antes de medir, como en el estudio 1.

**Comprobado en Trading 212 (13/10, busqueda por ISIN del propietario; sin comprar nada):** los 9 estan, en euros.

| # | Linea en Trading 212 (EUR) |
|---|---|
| 1 | SXR8, Xetra |
| 2 | EUNK, Xetra |
| 3 | IEMA, Amsterdam |
| 4 | EUNH, Xetra |
| 5 | IEAC, Londres (cotiza en EUR) |
| 6 | BTMA, Amsterdam |
| 7 | SGLD, Milan |
| 8 | AIGCP, Paris |
| 9 | IWDP, Amsterdam |

Junto a varios salen lineas "5X - CFD": nunca. Las fracciones de cada uno, por comprobar si se llega a operar.
