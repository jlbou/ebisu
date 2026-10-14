# Estudio 4: series montadas y comprobaciones antes de medir (14/10/2026)

Generado con `estudios/estudio4/bajar.py` y `estudios/estudio4/montar.py` (plan: `docs/plan-estudio-4.md` 3 y 13).
Skill: `data:validate-data`. **Solo correlaciones de rendimientos mensuales y calidad de datos: no se ha calculado
ningun rendimiento de ninguna estrategia ni de las piezas.**

## Comprobaciones (correlacion mensual >= 0,95)

| Serie reconstruida | Contra | Desde | Meses | Correlacion | Pasa |
|---|---|---|---|---|---|
| bolsa | estudio 1 (VTSMX/VGTSX) | 2000-08 | 313 | 0,995 | si |
| bolsa | EUNL.DE | 2009-09 | 204 | 0,976 | si |
| bolsa | VWCE.DE | 2019-07 | 86 | 0,977 | si |
| bolsa EE. UU. (USD, hasta 1996) | VTSMX | 1992-04 | 56 | 0,999 | si |
| bolsa (USD) | VT | 2008-06 | 219 | 0,990 | si |
| **bonos** | estudio 1 (VBMFX cubierto) | 2000-08 | 313 | **0,882** | **NO** |
| **bonos** | EUNA.DE | 2017-11 | 106 | **0,878** | **NO** |
| **bono a 7 anyos (USD)** | VBMFX | 1986-12 | 477 | **0,910** | **NO** |
| oro | 4GLD.DE | 2009-11 | 202 | 0,978 | si |
| monetario | XEON.DE | 2008-01 | 224 | 0,987 | si |
| oro de Frankfurt (medias, USD) | DataHub mensual | 1969-08 | 353 | 0,984 | si |
| tipo aleman (nivel) | EONIA | 1999-01 | 276 | 1,000 | si |
| Kenneth French Ind_all | MSCI EAFE con dividendos | 2001-01 | 300 | 0,996 | si |

**Bonos (diagnostico, sin rendimientos):** la formula del bono es correcta: contra fondos de bonos del Tesoro de EE. UU.
la correlacion mensual es **0,979 (VFITX, desde 1991) y 0,984 (IEF, desde 2002)** (0,886 contra VUSTX, de plazo
largo). Lo que no se parece es **el activo**: VBMFX y EUNA son indices agregados (empresas, hipotecas y, EUNA, todo el
mundo), no solo bonos del Tesoro. En el estudio 1 los bonos ya se aceptaron por debajo de 0,95 como limitacion conocida.
Segun el plan, se para y decide el propietario.

## Calidad de datos

- 01/07/1969 - 30/09/2026: 14.781 dias, sin duplicados, sin huecos, sin saltos de calendario de mas de 4 dias.
- Dias con movimientos de mas del 8 %: bolsa 7 (14/02/1973, devaluacion del dolar; octubre de 1987; 13/10/2008;
  marzo de 2020); oro 15 (1973-1983, la epoca de mas volatilidad del oro); bonos y monetario, ninguno. Todos son
  episodios conocidos, no errores.
- Empalmes: euro (04/01/1999) 0,1 %; bolsa mundial (02/01/1997) 0,9 %; EAFE con dividendos (02/01/2001) 3,5 %, que es
  la bolsa de EE. UU. de ese dia (-2,8 %) mas el cambio, y el precio de MSCI se mueve igual: no es un salto del empalme;
  GC=F (30/08/2000) 0,3 %.
