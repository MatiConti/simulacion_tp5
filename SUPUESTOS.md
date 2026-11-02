# Supuestos y decisiones de diseño — TP5 Simulación (Degustación C)

Este documento registra las decisiones que tomamos para resolver ambigüedades del
enunciado. Sirven como respaldo para la presentación (justificar el análisis) y
como referencia para no contradecirnos en el código.

## 1. Capacidades

- **Estacionamiento ("playa propia")**: capacidad infinita. El enunciado no
  indica un límite de lugares, por lo tanto no se modela cola de espera para
  estacionar: todo invitado que termina de acreditarse pasa directamente a
  estacionar.
- **Sala de degustación**: capacidad infinita. No hay límite de invitados
  simultáneos en la sala; por lo tanto no hay cola de espera para ingresar.
- **Conclusión**: las únicas colas del sistema son dos, y ambas existen porque
  hay un recurso limitado (servidores) que puede estar ocupado:
  1. Cola de acreditación (3 operarios de portón).
  2. Cola de entrevista de satisfacción (3 representantes).

## 2. Llegada de invitados sin estacionamiento (2.5 min)

- El enunciado da un único valor (2.5 min) sin "+/-" ni distribución nombrada,
  a diferencia de los invitados con auto (5 +/- 2, uniforme) y los tiempos de
  servicio (explícitamente exponenciales). Se interpreta como **tiempo entre
  llegadas determinístico/fijo**, no una variable aleatoria.

## 3. Tiempo de estacionar (3 min)

- Mismo criterio que el punto 2: valor único sin distribución indicada →
  **determinístico**, no es variable aleatoria.

## 4. Duración de la entrevista de satisfacción (dD/dt = P/5)

- Confirmado por la docente (Analía Daniele, mail del curso): `D` es la demora
  acumulada de la entrevista. Se integra numéricamente (Euler, paso `h`
  parametrizable) desde `D=0` con `dD/dt = P/5` hasta que `D` alcanza el valor
  de `P` (P=100 si usó estacionamiento, P=70 si es peatonal). El instante `t`
  en que esto ocurre es la duración de la entrevista.
- **No es una variable aleatoria generada por RND**: es un valor determinístico
  derivado de `P` mediante integración numérica. No se le asocia un número
  aleatorio en el vector de estado, pero sí debe mostrarse la integración
  numérica realizada (consigna general del TP).
- Nota matemática: al ser la tasa constante, analíticamente siempre da
  `t = 5` unidades de integración (= 50 min con la unidad por defecto de 10
  min), independientemente de si P=100 o P=70. Lo relevante para la consigna
  es la implementación genérica de Euler con `h` parametrizable, no que el
  resultado varíe entre ambos casos.

## 5. Objeto "Auto"

- No se modela como objeto temporal independiente. El estacionamiento es una
  etapa/atributo del objeto `Invitado` (tipo="auto"), no un objeto con
  comportamiento propio.

## 6. Cola de entrevista con abandono (reneging)

- Ambos tipos de invitado (auto y peatón) convergen en una única cola de
  entrevista, atendida por los 3 representantes, política FIFO.
- Un invitado abandona la cola (se retira sin responder la encuesta) si espera
  más de 5 minutos sin ser atendido por un representante.

## 7. Generador de números aleatorios

- Generador congruencial mixto: Semilla=1234, Constante multiplicativa=1714,
  Constante aditiva=1221, Módulo=3922.
- Es un único generador, compartido por todas las variables aleatorias del
  sistema (no uno por variable).

## 8. Ocupantes por auto

- Se evaluó agregar "cantidad de personas por auto" como extensión al modelo,
  pero el enunciado original no lo menciona en ningún punto (no hay referencia
  a pasajeros u ocupantes). Se descarta: cada invitado que llega en auto se
  modela como una unidad individual, tal como lo describe el enunciado
  ("Cada operario acredita a un invitado/coche por vez").

## 9. Decisiones técnicas del proyecto

- GUI: se empezó con PySide6, pero se migró a **Streamlit** para reutilizar el
  estilo visual (paleta, tarjetas KPI, secciones) de un TP anterior del mismo
  grupo. La tabla del vector de estado se renderiza con `streamlit.components.v1.html`
  (un iframe con HTML/CSS/JS propio): el encabezado anclado se logra con
  `position: sticky`, el scroll es nativo del navegador (sin parpadeos), y la
  selección de fila se resuelve con JavaScript puro en el cliente (sin volver
  a ejecutar el script de Streamlit), por lo que no se pierde al hacer scroll.
- `models/`, `eventos/`, `generador/` y `simulacion/` no dependen de la GUI,
  así que el cambio de framework no los afectó.
- La integración numérica de Euler (duración de la entrevista) se muestra
  como tabla (t, D) por invitado elegido, en la sección "Integración
  numérica" de la app. Se probó primero con un gráfico (Altair), pero se
  descartó por decisión propia a favor de la tabla; lo que exige el
  enunciado es que "la integración numérica de la parte continua también
  debe ser mostrada en la aplicación", sin pedir una forma específica.
- Vector de estado: se muestra en la interfaz **y** se puede exportar a Excel
  (openpyxl, vía botón de descarga), ambas opciones habilitadas.

---
*(Este archivo se va a seguir actualizando a medida que avancemos.)*
