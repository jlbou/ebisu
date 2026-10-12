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

### 3.1 Inventario hecho (12/10/2026): `docs/estudios/inventario-datos.md`

Sin mirar ningun rendimiento. Lo que sale:

- **Series largas con dividendos incluidos:** bolsa de EE. UU. desde **1980** (VFINX) y 1992 (VTSMX), bolsa
  internacional desde 1996 (VGTSX), bonos de EE. UU. desde **1986** (VBMFX). Con eso hay **~30 anyos** para las tres
  piezas juntas si el oro llega.
- **Oro:** el futuro desde **2000**, GLD desde 2004, Xetra-Gold (EUR) desde 2009. Antes de 2000 no hay oro diario en
  esta fuente: o el estudio empieza en 2000, o el oro anterior sale de otra fuente (p. ej. precios mensuales).
- **Vehiculos reales en euros:** EUNL/IWDA (bolsa mundial) desde 2009, EUNA (bonos cubiertos) desde 2017, VWCE desde
  2019, XEON (monetario en euros) desde 2008. Son de acumulacion: el "no ajustado" es lo esperado.
- **Monetario largo:** el tipo de la letra a 13 semanas de EE. UU. desde 1960 (es un tipo, no un precio).
- **Euro/dolar desde 2003** en esta fuente (un hueco de 18 dias en agosto de 2008). **Para 1999-2003 hay que ir a otra
  fuente** (el BCE o la Reserva Federal; antes de 1999, el marco aleman como aproximacion).
- **EWG2.DE no existe en Yahoo**; sobra (Xetra-Gold cubre el oro en euros).
- Huecos de 5-7 dias en todas: festivos y fines de semana largos, nada raro. La ultima fila de los de Xetra es de
  hoy (12/10), aun sin cerrar: el estudio solo usa dias cerrados.

**Para el criterio:** con oro diario, la ventana comun empieza en **2000**: ~26 anyos, que dan para una exploracion y
una reserva larga. Las series en dolares hay que pasarlas a euros (el inversor es de la zona euro).

## 4. Lo que cambia para la decision del vehiculo

| | Fondos con traspaso | ETF en Trading 212 |
|---|---|---|
| Impuestos | Ninguno hasta el final | En cada venta con ganancia |
| Automatico | **No** (clic manual, 5-8 dias habiles) | **Si** (API con demo) |
| Oro | **Practicamente no** | Si (ETC en euros) |
| Coste por operar | 0 € | 0 € (sin cambio de divisa si cotiza en euros) |
| Supervisor | Entidades espanyolas (CNMV) | Extranjero (Chipre o Alemania; por verificar) |

## 5. Segunda ronda (12/10): los puntos 1-3 de la lista, solo lectura

**5.1 Con que entidad de Trading 212 se contrata.** Dos fuentes espanyolas (Rankia, Finantres) dicen que un residente
en Espanya abre cuenta con **Trading 212 EU GmbH** (Alemania, supervisada por la **BaFin**); otra (Awake Trader), con la
chipriota o la bulgara. En el registro de la CNMV aparecen tres entidades del grupo como empresas extranjeras en libre
prestacion: Trading 212 Ltd (n.º 3044), Trading 212 Markets Ltd (n.º 5059) y **Trading 212 EU GmbH (n.º 5014)** (segun
Finantres, a 11/05/2026). **Lo mas probable: la alemana, con la BaFin; no la CNMV.** Solo se confirma en los documentos
legales de la propia cuenta (al abrir el demo se pueden leer).

**5.2 ETF en euros en Trading 212 (Xetra).** Fuentes de terceros (la mas reciente, de julio de 2026):

| Pieza | Candidato | Visto en Trading 212 |
|---|---|---|
| Bolsa mundial | Vanguard FTSE All-World (VWCE), acumulacion, 0,19 % al anyo | Si (guia de 07/2026) |
| Bonos | iShares Core Global Aggregate Bond, cubierto a euros, acumulacion (EUNA) | Si (guia de 07/2026) |
| Oro | db Physical Gold ETC en euros, o Invesco Physical Gold ETC | En una lista de la comunidad sin fecha: **por confirmar** |
| Monetario | Xtrackers EUR Overnight Rate Swap (XEON), cotiza en Xetra | **No confirmado** en Trading 212 |

Los cuatro existen en Xetra en euros; falta confirmar en la app el oro y el monetario (sin dinero: buscando el ISIN).

**5.3 Fondos indexados traspasables.**
- **Bolsa mundial: si, varios.** MyInvestor dice ofrecer los indexados de Vanguard, iShares, Fidelity, Amundi y NN **sin
  minimo**; ejemplos citados por terceros: iShares Developed World Index (0,12 %), Fidelity MSCI World Index (0,12 %),
  Vanguard Global Stock Index (0,18 %). Sin contrastar con la ficha oficial.
- **Bonos: existen** (p. ej. Vanguard Global Bond Index cubierto a euros, ~0,15 %), pero las clases encontradas tienen
  minimos institucionales; falta ver que clase vende una plataforma minorista.
- **Monetario:** no se encontro un indexado concreto; hay monetarios gestionados en las plataformas (por verificar).
- **Oro: no hay.** Los fondos de oro traspasables invierten en **mineras** (acciones de empresas, no el metal); el unico
  "sin mineras" encontrado mezcla oro, plata, platino y paladio (Ofi Invest Precious Metals, sin confirmar si es
  traspasable). **Confirmado lo que se sospechaba: con fondos, el oro se queda fuera.**
- Una fuente cita una consulta de Hacienda (DGT) que abriria el traspaso a algunos ETF UCITS, pero la ley 11/2021 los
  excluyo; **se trata como "los ETF no se traspasan"** salvo que se confirme lo contrario con la norma.

## 5.4 Los documentos de alta de Trading 212 (leidos el 12/10/2026, al abrir la cuenta)

Once documentos que la app pide aceptar: garantias (inversor y depositos), cuentas omnibus, condiciones de Invest,
politica de ejecucion, aviso de divulgacion, privacidad, cookies y la privacidad del verificador de identidad
(Fourthline). Lo que importa para Ebisu:

- **Entidad, CONFIRMADA:** Trading 212 EU GmbH, Ratingen (Alemania), **BaFin n.º 10109603**. Ley y tribunales alemanes.
- **Garantias:** valores, el 90 % hasta **20.000 €** (fondo alemán EdW); efectivo en cuentas omnibus en **J.P. Morgan
  SE y Sparkasse**, hasta **100.000 €** por banco. No cubren perdidas de mercado.
- **Custodia:** las inversiones estan en cuentas omnibus con subcustodios (a menudo fuera de Alemania); el derecho del
  cliente es **contractual** (entrega de valores iguales), no copropiedad directa. En una quiebra de un subcustodio
  se podria compartir un deficit. Riesgo bajo, pero real.
- **Ejecucion:** sin comision; las ordenes van a Trading 212 IE (Irlanda, del grupo), que puede ejecutarlas **contra si
  misma** (internalizador sistematico), sobre todo las fracciones. Conflicto de intereses declarado; "mejor ejecucion".
- **Fracciones:** no se pueden traspasar a otro broker; **cerrar la cuenta las vende** (y eso tributa).
- **Divisa principal: se elige al abrir y NO se puede cambiar.** Tiene que ser **EUR** (la API solo opera en la
  divisa principal; los ETF elegidos cotizan en euros).
- **Sin ventas en corto ni margen** en la cuenta Invest; orden maxima, el 95 % de lo disponible.
- **Impuestos:** a un residente fuera de Alemania **no le retienen**; dan un resumen anual. Todo se declara en la renta.
- **Intereses del efectivo:** solo si se activa el programa de reparto de intereses (si no, se los quedan). Los
  intereses tributan como rendimientos del capital.
- **Cierre:** pueden cerrar una cuenta con saldo 0 y sin operaciones durante 6 meses; cambios del contrato con 30 dias
  de aviso.
- **Datos personales:** se guardan 10 anyos tras cerrar (ley contra el blanqueo); el verificador de identidad trata
  datos biometricos (selfie) por obligacion legal. No venden datos a terceros para marketing sin consentimiento.
- **Cookies:** solo son obligatorias las esenciales y de rendimiento; las de publicidad se pueden rechazar.
- **La API no aparece en las condiciones:** tiene sus propias condiciones (por leer al generar la clave).

## 5.5 Respuesta del soporte de Trading 212 (12/10/2026)

La cuenta del propietario es Invest con Trading 212 EU GmbH (identidad ya verificada). Pregunta por el chat de soporte:
si hay cuenta de practica y como se saca su clave de API. Respuesta (resumida):

- **La cuenta de practica (demo) NO esta disponible para clientes de Trading 212 EU GmbH.**
- La API solo es para cuentas Invest; la clave de la cuenta real y la de practica pueden ser versiones distintas.

**Consecuencias:**
- Las pruebas de la API con ordenes no se pueden hacer con dinero ficticio en Trading 212. El papel de Ebisu (si una
  estrategia pasa) sera **papel propio**, simulado por el bot con precios reales, como en Ploutos.
- Lo que falta de la API (ordenes que acepta, oro y monetario en euros) solo se puede comprobar con la **cuenta real**:
  con una clave de solo lectura y sin dinero (sin ordenes), o con ordenes reales de importe minimo. Las dos son
  decision del propietario.

## 5.6 Instrumentos en Trading 212 y respuesta del bot de soporte (12/10/2026)

Buscados por ISIN en la app por el propietario (sin comprar nada):

| Pieza | Instrumento | ISIN | En Trading 212 |
|---|---|---|---|
| Bolsa | Vanguard FTSE All-World (Acc), VWCE | IE00BK5BQT80 | **Si**, Xetra, EUR |
| Bolsa | iShares Core MSCI World (Acc), EUNL | IE00B4L5Y983 | **Si**, Xetra, EUR |
| Bonos | iShares Core Global Aggregate Bond EUR Hedged (Acc), EUNA | IE00BDBRDM35 | **Si**, Xetra, EUR |
| Oro | Xetra-Gold | DE000A0S9GB0 | **No** |
| Oro | Xtrackers Physical Gold ETC | DE000A1E0HR8 | **No** |
| Oro | EUWAX Gold II | DE000EWG2LD7 | **No** |
| Oro | **Invesco Physical Gold (Acc), SGLD** | IE00B579F325 | **Si, Borsa Italiana (MIL), EUR** |
| Oro | iShares Physical Gold, EGLN | IE00B4ND3602 | Si, Londres (LSE), en EUR |
| Monetario | Xtrackers II EUR Overnight Rate Swap (Acc), XEON | LU0290358497 | **Si**, Xetra, EUR |

- **Oro: el candidato pasa a ser Invesco Physical Gold en Milan (EUR).** No cambia el estudio (los datos del oro son
  los mismos); el coste supuesto del 0,25 % al anyo para el oro sigue siendo conservador.
- **Cuidado:** al buscar salen tambien lineas "5X - CFD" (CFD apalancados 5 veces). **Nunca** se compran: solo la
  linea de la bolsa (XETR, MIL). Cuando haya bot, regla dura en el codigo.
- **Bot de soporte sobre la API:** la cuenta real admite **ordenes de mercado** por la API; de los demas tipos, de
  las fracciones por API, de las claves de solo lectura y de los limites de peticiones no sabe nada (se puede
  preguntar a un agente si hace falta). **Unica comision de Trading 212: el 0,15 % al cambiar de divisa** (con
  instrumentos en euros y cuenta en euros, no se paga); las bolsas y Hacienda pueden cobrar lo suyo.
- **Por verificar si se llega a operar:** que las fracciones funcionen en estos cuatro; que la tasa italiana sobre
  transacciones no se aplique al ETC de oro (en principio solo grava acciones italianas).

## 5.7 Fondos indexados con traspaso para H1-F (12/10/2026; solo lectura, fuentes secundarias)

Plataforma de referencia: **MyInvestor** (Andbank Espanya): segun su web, **0 € por comprar, vender, custodiar y
traspasar**; minimo de **1 €** en los indexados (con excepciones: mirar la ficha de cada fondo). Los traspasos sin
impuestos solo entre fondos comercializados por entidades que operan en Espanya.

| Pieza | Candidato | ISIN | Gasto anual | Notas |
|---|---|---|---|---|
| Bolsa mundial | iShares Developed World Index Fund (IE) D Acc EUR | IE00BD0NCM55 | ~0,12 % | Citado en MyInvestor; minimo sin confirmar |
| Bolsa mundial | Vanguard Global Stock Index Fund EUR Acc | IE00B03HD191 | ~0,18 % | Rankia da un minimo de 1 M€ (de la gestora); MyInvestor dice quitar minimos de Vanguard |
| Bonos | Vanguard Global Bond Index Fund EUR Hedged Acc | IE00B18GC888 | ~0,15 % | Visto en MyInvestor en fuentes de 2025-2026 (otras mas antiguas decian que no) |
| Monetario | AXA Tresor Court Terme C | FR0000447823 | ~0,04 % de gestion | Fondo monetario en euros, sin suscripcion ni reembolso |
| Monetario | Groupama Tresorerie IC | FR0000989626 | ~0,11 % de gestion | Alternativa |
| Oro | - | - | - | **No hay** fondo de oro traspasable (solo mineras): H1-F va sin oro, como fija el criterio |

- El criterio supone un gasto del 0,15 % al anyo para los fondos: encaja (el monetario seria mas barato: conservador).
- **Por verificar (solo si gana H1-F):** en la ficha de MyInvestor de cada ISIN, el minimo real, que sea traspasable y
  la clase exacta. Se puede mirar en su buscador publico sin abrir cuenta.

## 6. Pendiente de verificar (antes de fijar el criterio)

1. ~~Entidad de Trading 212~~: **confirmada, Trading 212 EU GmbH (BaFin)** (5.4).
2. Que ordenes acepta de verdad la API en real (se ve en el demo, sin dinero; la cuenta la abriria el propietario).
3. En la app de Trading 212: si estan el ETC de oro y el monetario en euros.
4. En la plataforma de fondos: la clase minorista de un indexado de bonos y un monetario, con sus costes.
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
  [Rankia](https://www.rankia.com/brokers/trading-212),
  [Finantres, mejores ETF en Trading 212 (07/2026)](https://finantresnoticias.com/etfs/trading-212-etf/),
  [comunidad de Trading 212, ETF en euros](https://community.trading212.com/t/request-add-these-eur-denominated-etfs/34572),
  [TradingView, XEON en Xetra](https://www.tradingview.com/symbols/XETR-XEON/chart),
  [Deutsche Borse, ETC de oro de Xtrackers](https://www.deutsche-boerse-cash-market.com/dbcm-en/newsroom/press-releases/New-Xtrackers-ETC-on-Xetra-Direct-access-to-gold-2019456).
- Fondos: [MyInvestor, indexados de iShares](https://myinvestor.es/inversion/fondos-indexados/myinvestor-blackrock/),
  [Bankkers, mejores indexados](https://bankkers.com/inversion/fondos/indexados/),
  [Finect, Vanguard Global Bond Index EUR Hedged](https://www.finect.com/fondos-inversion/IE00BN6QDH02-Vanguard_global_bond_index_eur_h_dist),
  [Openbank, fondos de oro](https://www.openbank.es/inversiones/fondos-de-oro),
  [Finect, como invertir en oro en 2026](https://www.finect.com/usuario/Josetrecet/articulos/Como_invertir_en_oro_y_plata),
  [EY, los ETF de la UE salen del regimen de traspasos (2021)](https://globaltaxnews.ey.com/news/2021-5775-spain-eu-etfs-no-longer-qualify-for-traspasos-regime),
  [guia fiscal de ETF 2026](https://guiafiscal.es/inversiones/etf-fiscalidad-2026-guia/).
- Datos: [BEKKs, StocksBonds (R)](https://search.r-project.org/CRAN/refmans/BEKKs/html/StocksBonds.html).
