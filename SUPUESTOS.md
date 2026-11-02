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
- P es parametrizable (valores en rojo del enunciado) y se asigna a cada
  invitado al crearlo según su tipo.
- La comparación `D >= P` usa una tolerancia de 1e-9 para que el error de
  redondeo de sumar `h·P/5` muchas veces no agregue un paso de más.
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
- El porcentaje de invitados que se retiran sin encuesta se calcula sobre los
  invitados que ya se retiraron (con o sin encuesta). Los que al terminar la
  simulación siguen esperando o en entrevista no entran en la cuenta porque
  todavía no se sabe cómo terminan.

## 7. Generador de números aleatorios

- Generador congruencial mixto: Semilla=1234, Constante multiplicativa=1714,
  Constante aditiva=1221, Módulo=3922.
- Es un único generador, compartido por todas las variables aleatorias del
  sistema (no uno por variable).

## 7 bis. Período del generador

- Con estos parámetros el generador repite la secuencia cada 468 números:
  1221 y 3922 comparten el factor 37 y 1713 (a−1) no es divisible por 2, 37
  ni 53, así que no cumple las condiciones de Hull–Dobell para período
  completo. Son los parámetros fijados por la consigna; se mantienen.

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
  (openpyxl, vía botón de descarga), ambas opciones habilitadas. El Excel
  exporta las filas visibles (i desde j + fila de X), no las 100.000, para
  que la descarga sea liviana; incluye una hoja con las integraciones de
  Euler de esos invitados.
- Al cortar por tiempo se agrega una fila final con el reloj en X (sin
  procesar eventos nuevos), y el tiempo ocioso de los operarios se cierra en X.

---
*(Este archivo se va a seguir actualizando a medida que avancemos.)*
