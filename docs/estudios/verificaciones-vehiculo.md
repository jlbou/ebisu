# Verificaciones antes del criterio: fondos con traspaso, broker con API y datos (12/10/2026)

**Solo lectura de fuentes publicas; no se ha abierto ninguna cuenta ni pedido ninguna clave.** Muchas fuentes son
comparadores o foros: se dice el nivel de cada una. Lo que no se ha podido confirmar, se dice.

## 1. Fondos indexados con traspaso

**Lo confirmado:**
- **El traspaso entre fondos no tributa:** el impuesto se aplaza hasta el reembolso final (art. 94 LIRPF). Para un
  fondo extranjero hace falta que sea **UCITS, domiciliado en la UE e inscrito en la CNMV**, y que se opere con
  comercializadoras inscritas en la CNMV (guia fiscal).
- **Los ETF, los fondos cotizados y los ETC quedan fuera:** su venta tributa siempre.
- **Plazo (CNMV):** hasta **5 dias habiles** si es la misma gestora o comercializadora, y hasta **8** con entidades
  distintas. MyInvestor habla de un maximo de 10 dias en un caso concreto (su cartera de metales).
- Plataformas con fondos indexados traspasables en Espanya: MyInvestor y Trade Republic (desde 2025), entre otras.

**El hallazgo importante: el oro casi no cabe en los fondos con traspaso.**
- La forma habitual de tener oro (un ETC, p. ej. iShares Physical Gold) **no es un fondo**: son titulos de deuda
  respaldados por oro que cotizan en bolsa. No se pueden traspasar.
- Un fondo UCITS no puede tener todo en un solo activo (reglas de diversificacion; dato de memoria, por verificar), asi
  que un "fondo indexado de oro" puro traspasable probablemente no existe. Los fondos de **mineras** de oro no son oro.
- **Consecuencia:** con fondos, el conjunto seria **bolsa + bonos + monetario, sin oro**; o el oro por fuera, con un
  ETC que tributa en cada venta.

**Sin confirmar:** el requisito de 500 participes para fondos extranjeros (solo aparece en foros, contradictorio);
que fondos concretos hay de bolsa mundial, bonos y monetario, y sus minimos.

**Automatizacion:** ninguna plataforma de fondos encontrada tiene API para operar. Con fondos, el bot da la senyal y el
traspaso se hace a mano.

## 2. Broker sin comision con fracciones de ETF y API: Trading 212

**Costes (reviews de terceros, coinciden):**
- **0 € de comision** en ETF y acciones de la UE; fracciones desde ~1 €.
- **Cambio de divisa: hasta el 0,15 % por lado** si el activo cotiza en otra moneda. Con ETF UCITS que coticen en euros
  (p. ej. en Xetra) no habria cambio.
- Sin custodia ni retiradas; las fracciones no se pueden traspasar a otro broker (solo las participaciones enteras).

**API (documentacion oficial, `docs.trading212.com`):**
- Existe una API publica, para cuentas **Invest** (no CFD), con entorno de **demo** y entorno real separados.
- Ordenes: de mercado, limitadas, stop y stop limitadas. La documentacion antigua decia que en real solo iban las de
  mercado; un anuncio posterior de la comunidad dice que ya van las cuatro. **Por comprobar en el demo.**
- **Solo en la moneda principal de la cuenta** (euros): encaja con ETF en euros.
- La clave se genera en la app (Ajustes > API); el secreto se ensenya una sola vez. La pondria el propietario en `.env`.

**Regulacion (fuentes no oficiales, se contradicen):**
- Trading 212 Markets Ltd (Chipre, CySEC) aparece en el registro de la CNMV como **entidad extranjera en libre
  prestacion de servicios**: opera en Espanya con permiso europeo, pero **la CNMV no es su supervisor principal**.
- Proteccion del inversor en Chipre: hasta **20.000 €**.
- Una fuente dice que a los clientes espanyoles los atiende Trading 212 EU GmbH (Alemania, BaFin); otra, la entidad
  chipriota o la bulgara. **Por verificar en el contrato** y en el buscador de entidades de la CNMV.

**Impuestos:** cada venta con ganancia tributa ese anyo; la regla de los dos meses se aplica a los ETF. Un broker
extranjero **no retiene**: las ganancias se declaran a mano en la renta (el bot preparara el resumen).

## 3. Datos historicos gratuitos

- **ETF en Yahoo Finance (yfinance) o Stooq:** gratis y diarios, pero cortos para lo que pide el estudio: el ETF de
  MSCI World de EE. UU. desde 2012, el de oro desde 2004, el de bonos agregados desde 2003 (fechas de memoria y de una
  fuente secundaria, **por comprobar**).
- **Indices largos** (MSCI World, bonos con cupones reinvertidos): casi siempre de pago. Hay series academicas
  gratuitas (p. ej. MSCI World diario desde 1995 en un paquete de R) y fondos con mucha historia para empalmar.
- **Oro:** historia diaria larga y gratuita bastante facil de conseguir.
- **Para la reserva larga** que pidio el council (decision 2) hacen falta **~20 anyos o mas**: habra que empalmar
  series y decir como en el criterio.

## 4. Lo que cambia para la decision del vehiculo

| | Fondos con traspaso | ETF en Trading 212 |
|---|---|---|
| Impuestos | Ninguno hasta el final | En cada venta con ganancia |
| Automatico | **No** (clic manual, 5-8 dias habiles) | **Si** (API con demo) |
| Oro | **Practicamente no** | Si (ETC en euros) |
| Coste por operar | 0 € | 0 € (sin cambio de divisa si cotiza en euros) |
| Supervisor | Entidades espanyolas (CNMV) | Extranjero (Chipre o Alemania; por verificar) |

## 5. Pendiente de verificar (antes de fijar el criterio)

1. Que entidad de Trading 212 contrata con clientes espanyoles, y su registro en la CNMV.
2. Que ordenes acepta de verdad la API en real (se puede ver en el demo, sin dinero).
3. Que ETF UCITS en euros hay en Trading 212 para bolsa mundial, bonos, oro y monetario.
4. Que fondos indexados traspasables concretos hay para bolsa, bonos y monetario, y si existe alguno de oro.
5. Las fuentes de datos: primera fecha y si los precios incluyen dividendos (requiere bajar datos).

## Fuentes (leidas el 12/10/2026)

- Traspasos: [guia fiscal de fondos 2026](https://guiafiscal.es/inversiones/fondos-de-inversion-fiscalidad-2026-guia/),
  [Economipedia, fiscalidad 2026](https://economipedia.com/guia/cuanto-pagas-a-hacienda-por-invertir),
  [Bankkers, plataformas de fondos indexados](https://bankkers.com/inversion/mejores-plataformas-fondos-indexados/),
  [Finantres, cartera de metales de MyInvestor](https://finantresnoticias.com/bancos/detalle-debes-comprobar-antes-sacar-cartera-metal-myinvestor/),
  [Finect, foro sobre traspasos y participes](https://www.finect.com/preguntas/653/que-bancos-permiten-hacer-traspasos-con-smart-social-sicav).
- Oro: [iShares Physical Gold ETC (BlackRock)](https://www.blackrock.com/uk/individual/products/258441/ishares-physical-gold-etc-fund).
- Trading 212: [documentacion de la API](https://docs.trading212.com/api/orders),
  [comunidad de Trading 212](https://community.trading212.com/t/trading-212-api-update/87988?page=8),
  [BrokerChooser](https://www.brokerchooser.com/broker-reviews/trading-212-review),
  [Curvo](https://curvo.eu/article/trading-212-review),
  [Finantres, Trading 212 y la CNMV](https://finantres.com/trading-212-cnmv/),
  [Awake Trader](https://www.awaketrader.com/educacion/trading-212-espana-review),
  [Rankia](https://www.rankia.com/brokers/trading-212).
- Datos: [BEKKs, StocksBonds (R)](https://search.r-project.org/CRAN/refmans/BEKKs/html/StocksBonds.html).
