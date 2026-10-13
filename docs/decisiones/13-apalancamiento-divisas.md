# Decision 13: apalancamiento solo en divisas, con un liston de riesgo (13/10/2026; fijado ANTES de medir)

Cambia la decision 5 (sin apalancamiento) **solo para el estudio 3 de divisas**. El resto de Ebisu sigue a 1x.

## 13.1 Por que

- El propietario prefiere las divisas y no pondra mas de 250 € (decision 3).
- El minimo del sector son 1.000 unidades (~1.000 €; `docs/estudios/verificaciones-vehiculo.md` 7): con 250 €,
  cualquier operacion de divisas es apalancada (~4x).
- En la UE, un particular no puede perder mas de lo ingresado (proteccion de saldo negativo): el peor caso son los
  250 €. El propietario lo acepta. Los stops pueden ejecutarse mucho mas abajo en un salto (franco suizo, 2015).

## 13.2 Limites (opcion B del propietario)

- El apalancamiento minimo imprescindible para llegar al minimo de 1.000 unidades (~4x), nunca mas.
- Una sola posicion abierta a la vez. **Cambiado el 13/10, antes de medir (opcion B del propietario):** exposicion total
  <= 4 veces la cuenta del dia y ninguna divisa repetida entre posiciones abiertas; con 250 € sigue siendo una sola.
- Perdida maxima por operacion y freno mensual (el bot se para y avisa): valores por decidir antes de medir.
- Calendario de eventos (bancos centrales, empleo de EE. UU., referendums y elecciones): esos dias no se opera.
- Dinero real solo si el estudio pasa (ganancia, no suerte y el liston de riesgo de 13.3) y despues el papel.

## 13.3 Liston de riesgo (opcion M del propietario)

Ademas de las condiciones de ganancia, la estrategia pasa solo si cumple las tres:

1. **Probabilidad de perder la mitad de la cuenta (bajar a 125 €) en algun momento de 3 anyos: menos del 3 %.**
2. **Peor caida historica de la cuenta: menos del 30 %.**
3. **Peor sorpresa no prevista (prueba de estres): pierde menos del 25 %.**

### Como se mide la probabilidad (1)

1. Se simula la estrategia en la reserva con todas las condiciones reales: ~4x, diferencial, intereses de cada noche,
   stops que se ejecutan peor en los saltos. Sale el resultado de cada dia, **sin** el freno mensual.
2. Se construyen **10.000 futuros posibles de 3 anyos** cosiendo **bloques de 20 dias habiles seguidos** escogidos al
   azar de la historia real (bootstrap por bloques). Los bloques mantienen juntos los dias malos, que vienen en rachas;
   barajar dias sueltos subestimaria el riesgo.
3. Cada futuro se recorre dia a dia desde 250 €, **aplicando el freno mensual y la perdida maxima**, y se mira si en
   algun momento la cuenta toca 125 €.
4. La probabilidad es la proporcion de futuros que tocan 125 €, con su intervalo de confianza al 95 %; pasa si el
   **extremo alto** del intervalo es menor que el 3 %.

Limite conocido: solo recombina lo que ya ha pasado; no inventa una crisis peor que la historica. Por eso existe la
condicion 3 (estres).
