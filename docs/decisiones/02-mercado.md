# Decision 2: el mercado (12/10/2026)

## Decidido (opcion A)

- **Mercado: bolsa, bonos y oro, siguiendo la tendencia** (la familia de L de Ploutos: dentro de lo que esta por encima
  de sus medias, fuera, en un monetario, de lo que no).
- **El vehiculo se decide despues, con el broker:** ETF en Interactive Brokers (automatico, pero cada venta con
  ganancia tributa ese anyo) o fondos indexados con traspasos (sin impuestos hasta el reembolso final, pero sin API: el
  bot da la senyal y el propietario hace el clic; 2-5 dias por traspaso).
- **La idea de una persona conocida del propietario entra en la lista de hipotesis del paso 2** (`docs/hipotesis.md`), con divisas y el mismo
  rigor. Las divisas no son el mercado principal.

## Por que

- Es donde mas pruebas hay de que seguir la tendencia funciona fuera de muestra (un siglo de datos en bolsa, bonos, oro
  y materias primas).
- El activo ya gana por si solo (la bolsa y los bonos pagan por mantenerlos): si la estrategia solo consigue caer menos,
  como L, aun puede ganar dinero. En divisas, no.
- Tres activos poco correlacionados dan mas oportunidades de tendencia que uno solo; opera poco (comisiones bajas).

## El council (12/10; Skeptic, Pragmatist y Critic, como subagentes sin la conversacion)

- **Consenso (4 de 4):** bolsa, bonos y oro con tendencia. **Divisas, descartadas por unanimidad** (suma cero; sin
  apalancamiento no hay rendimiento de fondo). El oro solo es una pieza del conjunto, no un mercado.
- **Lo que cambio la recomendacion: los impuestos.** Quien mantiene un indexado y lo cambia por traspasos no paga hasta
  el final; un bot con ETF paga en cada rotacion con ganancia (estimacion del Skeptic, sin comprobar: 1-2 puntos al anyo
  de desventaja frente al liston de la decision 1).
- **Discrepancia mas fuerte:** ETF (automatico) frente a fondos con traspasos (sin impuestos, con clic manual).
- **Premisa:** el Skeptic dice que la decision de fondo es el vehiculo, y que la respuesta honesta puede ser "ningun bot".

## Lo que se lleva al paso 2 (para el criterio, antes de medir)

- Impuestos **operacion por operacion** en la estrategia (con la regla de los dos meses en ETF); la referencia, el
  indexado mantenido **con** el diferimiento de los traspasos.
- Operar como mucho **mensual** si el capital es pequenyo (con 2.000 € y seis piezas, 1,25-3 € por orden es el 0,4-1 %).
- **Reserva mas larga que en Ploutos:** con ~12 decisiones al anyo, un anyo no distingue habilidad de suerte. Las ~30
  pruebas de Ploutos no cuentan aqui (otro mercado), pero cada variante de Ebisu si.
- Otra referencia sencilla (el Pragmatist): un indexado mundial + una pieza de oro, rebalanceados una vez al anyo.

## Por verificar

- Que existan los fondos necesarios con traspaso (los extranjeros, registrados en la CNMV con los requisitos), sus
  costes y cuanto tarda un traspaso de verdad.
