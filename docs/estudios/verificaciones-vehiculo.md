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
- **Respuesta de un agente del chat de Trading 212 (13/10/2026):**
  - Por la API de la cuenta real: ordenes **de mercado, limitadas, stop y stop limitadas**.
  - **Fracciones si** (p. ej. 0,5 participaciones), **pero no ordenes por importe en euros**: el bot tendra que
    calcular la cantidad (importe / precio) y redondearla a lo que admita cada instrumento.
  - **Claves de solo lectura posibles** con permisos concretos (p. ej. `orders:read`, `account`). **La API no permite
    retirar dinero** (lo mismo que la regla 19 de Ploutos).
  - Limites por cuenta y por punto de la API: p. ej. 50 peticiones por minuto para ordenes de mercado y una cada 2 s
    para limitadas. De sobra para una revision al mes (o a la semana).
  - VWCE, EUNA, XEON y SGLD: fracciones si el instrumento las tiene habilitadas; impuestos y costes de cada uno, en su
    ficha de la app o en los metadatos de la API. **La tasa italiana del oro sigue sin respuesta concreta**: mirarla en
    la ficha de SGLD si se llega a operar.

## 5.6 bis Bonos del Tesoro cubiertos para H1-M (14/10/2026)

Tras el estudio 4 (decision 15), la pieza de bonos pasa a ser bonos del Tesoro de EE. UU. a 7-10 anyos cubiertos a
euros. Buscados por ISIN en la app por el propietario (sin comprar nada): **los dos estan disponibles**.

| Instrumento | ISIN | En Trading 212 |
|---|---|---|
| iShares $ Treasury Bond 7-10yr UCITS ETF EUR Hedged (Acc), CEMF | IE000K1VI152 | **Si** (preferido) |
| iShares $ Treasury Bond 7-10yr UCITS ETF EUR Hedged (Dist), IBB1 | IE00BGPP6697 | **Si** (reserva) |

Sin anotar: la bolsa en que cotiza cada uno dentro de Trading 212 y si admite fracciones; se comprueba con los metadatos
de la API (cantidad minima por instrumento) al construir el bot.

## 5.6 ter Verificaciones de Trading 212 para H1-M (15/10/2026)

Hecho sin cuenta ni claves, con la documentacion oficial de la API y la de Hacienda de Italia (leidas el 15/10/2026).

**1. La API (documentacion oficial, [docs.trading212.com/api](https://docs.trading212.com/api), version 0, en "beta"):**
- **Ordenes por la API: de mercado, limitadas, stop y stop limitadas** (las cuatro tienen su punto en la seccion
  *Orders*). Coincide con lo que dijo el agente del chat (5.6).
- **Cantidad con decimales** (el ejemplo de la orden de mercado es `quantity: 0.1`). **Por importe en euros, no**: "Placing
  orders by value is not currently supported via the API". Coincide con el agente.
- **Solo en la moneda principal de la cuenta** y sin multidivisa por la API: con la cuenta en euros y los cuatro ETF en
  euros, encaja.
- **Una orden de mercado repetida puede duplicarse** ("this endpoint is not idempotent"). **Para el bot (si se llega a
  dinero real): regla dura**, nunca reintentar una orden sin comprobar antes en las pendientes y el historial que no
  se haya ejecutado.
- Las claves se pueden **restringir a unas IP** desde los ajustes de la cuenta.
- **El listado de instrumentos (`/equity/metadata/instruments`) NO dice si un ETF admite fracciones ni la cantidad
  minima** (da ticker, ISIN, moneda, tipo, cantidad maxima y horario de la bolsa). Lo que decia 5.6 bis ("se comprueba con
  los metadatos de la API") **ya no vale**: las fracciones se miran en la app (abajo).

**2. La tasa italiana sobre transacciones financieras y el oro (SGLD): NO se aplica.**
- Grava el traspaso de **acciones y otros instrumentos financieros participativos emitidos por sociedades residentes en
  Italia** (y los titulos que los representan), y los derivados cuyo subyacente son sobre todo esos instrumentos
  (ley 228/2012, art. 1, comas 491 y 492; [Agenzia delle Entrate, "Imposta sulle transazioni finanziarie - Che cos'e"](https://www.agenziaentrate.gov.it/portale/schede/pagamenti/imposta-sulle-transazioni-finanziarie/infogen-imposta-transazioni-finanziarie),
  actualizada el 17/03/2026; desde el 01/01/2026, el 0,4 % sobre acciones). Tambien
  [Borsa Italiana](https://www.borsaitaliana.it/azioni/notiziedettaglio/iftt.en.htm) (actualizacion de 12/2015).
- **SGLD (ISIN IE00B579F325) es un ETC de oro emitido por una sociedad irlandesa** (Invesco Physical Markets plc): no
  es una accion ni un instrumento participativo de una sociedad italiana, y su subyacente es oro. **Cotizar en Milan no
  lo mete en la tasa**: lo que cuenta es quien lo emite.
- No comprobado: la ficha de SGLD en la app de Trading 212 (por si Trading 212 cobrara algo propio). Mirarla antes de
  operar con dinero real.

**3. Bolsa, moneda y fracciones de las cuatro piezas (15/10/2026).** Buscadas por ISIN en la app por el propietario
(sin comprar nada) y en las paginas publicas de cada instrumento de Trading 212:

| Pieza | Linea correcta en Trading 212 | Bolsa | Moneda | Precio (15/10) | Pagina publica |
|---|---|---|---|---|---|
| Bolsa | VWCE · XETR | Deutsche Börse Xetra | EUR | 170,94 € | `/trading-instruments/invest/VWCE.DE` |
| Bonos | CEMF · XETR | Deutsche Börse Xetra | EUR | 4,9135 € | `/trading-instruments/invest/CEMF.DE` |
| Oro | SGLD · MIL | Borsa Italiana | EUR | 356,59 € | `/trading-instruments/invest/SGLD.IT` |
| Monetario | XEON · XETR | Deutsche Börse Xetra | EUR | 150,504 € | `/trading-instruments/invest/XEON.DE` |

- Coinciden con los precios del bot en papel (VWCE.DE, CEMF.DE, SGLD.MI y XEON.DE en Yahoo).
- **Fracciones:** la pagina publica de las cuatro dice "Compra y vende acciones fraccionarias desde solo 1 €". **No
  comprobado en la pantalla de la orden**: con la cuenta a cero, la app pide anyadir fondos antes de dejar ver la orden,
  y el texto de la pagina podria ser comun a todos los instrumentos. **Si se decide pasar a dinero real, lo primero
  (antes del bot): con el primer ingreso, comprobar en la orden que cada una admite una cantidad con decimales.** Sin
  fracciones, con 250 € no se podrian comprar VWCE, SGLD ni XEON en la proporcion de la regla.
- Al buscar VWCE sale tambien **"VWCE 5X · CFD"**, de nombre y precio casi iguales: **nunca**. Regla dura en el codigo.

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

## 7. Divisas: que broker podria operar el estudio 3 (13/10/2026, busqueda en la web; nada contratado)

Pregunta: operar divisas sin apalancamiento (1x), automatico (API) y con 250 €. Fuentes: paginas de cada broker y
terceros (leidas el 13/10/2026); lo marcado "sin confirmar" viene de terceros o foros.

| Broker (UE) | Como | API | Minimo por operacion | Coste | Con 250 € a 1x |
|---|---|---|---|---|---|
| Trading 212 | Solo CFD | La API publica es solo de Invest e ISA | - | - | No |
| Interactive Brokers | Divisa real (IDEAL, < 25.000 $) | Si | Sin minimo de tamanyo; comision 0,01 % con **minimo de 2,50 $** | + 1-2 pb de peor precio | No (comision ~1 %); viable desde ~12.000 € por orden |
| Dukascopy Europe | Al contado con margen | Si (JForex, FIX) | **1.000 unidades**; deposito minimo 100 $ | Diferencial + comision pequenya | No (1.000 € por compra = 4x); a 1x, ~1.000 € por par abierto |
| Capital.com (CySEC) | CFD | Si | 0,01 lotes (sin confirmar si son 1.000 unidades) | Diferencial | Igual que Dukascopy |
| IG Europe | CFD | Si (REST) | Contratos de 10.000-100.000 € segun pais (sin confirmar para Espanya) | Diferencial | No |
| Saxo | Al contado con margen | Si (OpenAPI) | Sin confirmar; comision minima 1-3 $ | Diferencial + comision | Probablemente no |
| eToro | CFD | API publica desde 10/2025; no consta que cubra divisas | **1.000 $** en divisas (sin fecha) | Diferencial | No |
| OANDA (UE: OANDA TMS, Varsovia) | CFD | La API v20 no esta para la UE (foro; la nota oficial solo cita MT5 y web) | 1 unidad fuera de la UE | Diferencial | No (sin API) |
| XTB | CFD | **API cerrada el 14/03/2025** | - | - | No |
| Brokers con MetaTrader 5 (p. ej. IC Markets EU) | CFD | MT5 con el paquete de Python (solo Windows) | 0,01 lotes = 1.000 unidades | Diferencial (+ comision) | Igual que Dukascopy |

**Conclusion:** el minimo del sector son **1.000 unidades** (~1.000 €). Los "nano lotes" (100 unidades) solo aparecen en
brokers sin regulacion de la UE (foros): descartados. A 1x hacen falta ~1.000 € por par abierto a la vez; con 250 €,
cualquier operacion de divisas ya es apalancada. Es una cuestion de capital, no de estrategia.

Fuentes: [Trading 212, API](https://helpcentre.trading212.com/hc/en-us/articles/14584770928157-Trading-212-API-key);
[IBKR, comisiones](https://www.interactivebrokers.com/download/newMark/PDFs/commissionsForex.pdf) y
[ordenes pequenyas](https://ibkb.interactivebrokers.com/tag/forex?page=2);
[Dukascopy, cuentas](https://www.dukascopy.com/swiss/spanish/forex/forex_trading_accounts/);
[Capital.com](https://help.capital.com/hc/en-us/articles/4403989787538-What-is-the-minimum-trade-size);
[IG, EUR/USD](https://www.ig.com/uk/forex/markets-forex/eur-usd);
[Saxo](https://www.home.saxo/rates-and-conditions/forex/trading-conditions);
[eToro, minimos](https://etoro.com/news-and-analysis/etoro-updates/introducing-lower-unified-minimum-trade-sizes) y
[API](https://www.etoro.com/news-and-analysis/press-releases/etoro-marks-15-years-of-social-investing-with-launch-of-public-apis-and-expansion-of-copytradertm-to-the-us/);
[OANDA UE](https://www.oanda.com/group/media-center/press-releases/new-operations-in-the-eu) y
[foro](https://www.forexpeacearmy.com/community/threads/what-broker-after-oanda-eu-client-rest-api.79944/post-452044);
[XTB](https://www.xtb.com/en/help-center/our-platforms/does-xtb-offer-investment-automation-tools);
[nano lotes, foro](https://forums.babypips.com/t/europe-broker-with-nano-lots-or-units/1261989).
