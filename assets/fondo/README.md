# Fondo del panel: Ebisu en relieve

`ebisu-relieve.png` es el dibujo de lineas de Ebisu (con el pargo y la cana) grabado en relieve, para el fondo fijo del
panel (`ebisu/panel.py`, servido en `/fondo-ebisu.png`).

- **Origen:** una ilustracion de Ebisu que aporto el propietario (17/10/2026), que dice que no tiene copyright. Solo se
  guarda el resultado, no la imagen original.
- **Como se hizo** (sin dependencias nuevas, con numpy y scipy): bordes de la imagen (Sobel en cada canal de color), solo
  dentro de una mascara aproximada del personaje, la cana y la roca (la roca, con menos detalle); el contorno de la
  mascara se difumina para que el dibujo se disuelva en el fondo sin corte; despues se genera el relieve (una vora
  clara arriba a la izquierda y una sombra abajo a la derecha) en una imagen en gris con transparencia, 720 x 720 px.
- Se guarda un dia en el navegador (`Cache-Control`), porque no cambia.
