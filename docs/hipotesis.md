# Hipotesis para el paso 2

Lista abierta hasta que se fije el criterio del estudio. **Ninguna se ha medido.** Cada una que se pruebe cuenta como
variante para el liston contra la suerte (Sharpe deflactado).

| # | Hipotesis | Mercado | Origen | Notas |
|---|---|---|---|---|
| 1 | Seguir la tendencia (familia de L: medias de 20/50/100/200 dias), rotando entre bolsa, bonos y oro, con un monetario de refugio | ETF o fondos indexados europeos | Ploutos (L) y la literatura | La principal (decision 2) |
| 2 | Operar en rango del dia anterior: comprar por debajo del minimo de ayer, vender cerca del maximo de ayer | Divisas (p. ej. USD/CAD) | Una persona conocida del propietario que opera divisas (12/10) | Es reversion a la media, lo contrario de la tendencia; en Ploutos la reversion perdio siempre. Sin apalancamiento la ganancia por operacion es minima. Datos gratuitos; facil de programar |
| 3 | Kronos (modelo de prediccion de velas) | Divisas y/o ETF | Ploutos (en cripto no acerto) | Opcional; entorno guardado en `Ploutos/var/kronos/` |
| 4 | La IA como filtro de riesgo: lee noticias y puede reducir o aplazar una compra de la estrategia que pase, nunca anyadir riesgo | El de la estrategia que pase | Decision 8 (12/10) | **No se puede probar con la historia** (la IA ya sabe lo que paso): solo en papel hacia adelante, contra el bot sin IA. No cuenta como variante de la historia |
