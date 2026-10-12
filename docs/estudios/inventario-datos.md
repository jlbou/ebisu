# Inventario de datos historicos (2026-10-12)

Generado por `estudios/inventario/inventario.py` con yfinance (no oficial). **Solo fechas, huecos y ajuste:
no se ha calculado ningun rendimiento ni se ha mirado ninguna curva** (para no contaminar la reserva).

- *Faltan*: dias habiles (lunes a viernes) sin precio entre la primera y la ultima fecha; incluye festivos.
- *Hueco mayor*: el salto mas largo entre dos fechas con precio.
- *Ajuste*: si el precio ajustado difiere del cierre (dividendos o cupones incluidos). Un ETF de acumulacion,
  un futuro o un tipo de cambio no reparten: "no" es lo esperado ahi.

| Pieza | Tipo | Ticker | Que es | Primera | Ultima | Filas | Faltan | Hueco mayor | Ajuste |
|---|---|---|---|---|---|---|---|---|---|
| Bolsa | larga | `VFINX` | Vanguard 500 Index (fondo, EE. UU.) | 1980-01-02 | 2026-10-09 | 11789 | 414 (3.4%) | 7 dias | si (repartos) |
| Bolsa | larga | `VTSMX` | Vanguard Total Stock Market Index (fondo, EE. UU.) | 1992-04-27 | 2026-10-09 | 8675 | 315 (3.5%) | 7 dias | si (repartos) |
| Bolsa | larga | `VGTSX` | Vanguard Total International Stock Index (fondo) | 1996-04-29 | 2026-10-09 | 7662 | 283 (3.6%) | 7 dias | si (repartos) |
| Bolsa | larga | `VT` | Vanguard Total World Stock ETF (EE. UU.) | 2008-06-26 | 2026-10-09 | 4601 | 171 (3.6%) | 5 dias | si (repartos) |
| Bolsa | larga | `ACWI` | iShares MSCI ACWI ETF (EE. UU.) | 2008-03-28 | 2026-10-09 | 4664 | 172 (3.6%) | 5 dias | si (repartos) |
| Bolsa | larga | `URTH` | iShares MSCI World ETF (EE. UU.) | 2012-01-12 | 2026-10-09 | 3707 | 140 (3.6%) | 5 dias | si (repartos) |
| Bolsa | real | `VWCE.DE` | Vanguard FTSE All-World UCITS, acumulacion (Xetra, EUR) | 2019-07-29 | 2026-10-12 | 1832 | 49 (2.6%) | 6 dias | no (igual al cierre) |
| Bolsa | real | `EUNL.DE` | iShares Core MSCI World UCITS (Xetra, EUR) | 2009-09-25 | 2026-10-12 | 4328 | 119 (2.7%) | 6 dias | no (igual al cierre) |
| Bolsa | real | `IWDA.AS` | iShares Core MSCI World UCITS (Amsterdam, EUR) | 2009-09-25 | 2026-10-12 | 4362 | 85 (1.9%) | 5 dias | no (igual al cierre) |
| Bonos | larga | `VBMFX` | Vanguard Total Bond Market Index (fondo, EE. UU.) | 1986-12-11 | 2026-10-09 | 10033 | 359 (3.5%) | 7 dias | si (repartos) |
| Bonos | larga | `AGG` | iShares Core US Aggregate Bond ETF | 2003-09-29 | 2026-10-09 | 5795 | 215 (3.6%) | 5 dias | si (repartos) |
| Bonos | larga | `BNDX` | Vanguard Total International Bond ETF (cubierto a USD) | 2013-06-04 | 2026-10-09 | 3359 | 125 (3.6%) | 4 dias | si (repartos) |
| Bonos | real | `EUNA.DE` | iShares Core Global Aggregate Bond UCITS, cubierto a EUR (Xetra) | 2017-11-21 | 2026-10-12 | 2256 | 64 (2.8%) | 6 dias | no (igual al cierre) |
| Oro | larga | `GC=F` | Futuro del oro (COMEX, continuo) | 2000-08-30 | 2026-10-12 | 6554 | 260 (3.8%) | 5 dias | no (igual al cierre) |
| Oro | larga | `GLD` | SPDR Gold Shares (EE. UU.) | 2004-11-18 | 2026-10-09 | 5507 | 205 (3.6%) | 5 dias | no (igual al cierre) |
| Oro | real | `4GLD.DE` | Xetra-Gold (EUR) | 2009-11-13 | 2026-10-12 | 4291 | 121 (2.7%) | 6 dias | no (igual al cierre) |
| Oro | real | `EWG2.DE` | EUWAX Gold II (EUR) | - | - | 0 | - | - | sin datos |
| Monetario | larga | `^IRX` | Rentabilidad de la letra del Tesoro de EE. UU. a 13 semanas (un tipo, no un precio) | 1960-01-04 | 2026-10-09 | 16678 | 742 (4.3%) | 7 dias | no (igual al cierre) |
| Monetario | larga | `BIL` | SPDR Bloomberg 1-3 Month T-Bill ETF | 2007-05-30 | 2026-10-09 | 4873 | 180 (3.6%) | 5 dias | si (repartos) |
| Monetario | real | `XEON.DE` | Xtrackers II EUR Overnight Rate Swap UCITS (Xetra, EUR) | 2008-01-02 | 2026-10-12 | 4771 | 128 (2.6%) | 6 dias | no (igual al cierre) |
| Divisa | larga | `EURUSD=X` | Cambio euro/dolar | 2003-12-01 | 2026-10-12 | 5932 | 34 (0.6%) | 18 dias | no (igual al cierre) |
