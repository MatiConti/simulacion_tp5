# Guía para defender el código — TP5 Simulación

Este documento es para que puedas explicar el proyecto en la presentación
sin tener que releer todo el código. Está pensado como un repaso antes de
defender, no como documentación técnica exhaustiva (para eso están los
comentarios del código y [SUPUESTOS.md](SUPUESTOS.md)).

---

## 1. El modelo en una frase

Simulamos un evento de degustación con **dos colas con servidores
múltiples** (acreditación en el portón con 3 operarios, y entrevista de
satisfacción con 3 representantes), conectadas por tres etapas intermedias
sin cola (estacionar, estar en la sala de degustación) porque tienen
capacidad infinita.

Dibujalo así si te lo piden en el pizarrón:

```
Invitado con auto:
  llega -> [cola] -> acredita (3 operarios) -> estaciona (3 min fijo)
         -> sala de degustación (exp. 20 min) -> [cola] -> entrevista (3 repr.)
         -> se va

Invitado peatón:
  llega -> sala de degustación (exp. 20 min) -> [cola] -> entrevista (3 repr.)
         -> se va

En la cola de entrevista: si espera más de 5 min sin ser atendido, abandona.
```

## 2. Por qué el proyecto está dividido así

La idea central es que **la lógica de la simulación no sabe que existe una
interfaz gráfica**. Separamos en capas:

| Carpeta | Qué contiene | Depende de |
|---|---|---|
| `models/` | Los objetos del enunciado (Invitado, Operario, Representante, Cola, FilaVectorEstado) | nada |
| `eventos/` | Qué es un evento y la lista de eventos futuros (FEL) | nada |
| `generador/` | El generador de números aleatorios y las distribuciones | nada |
| `simulacion/` | El motor que ata todo lo anterior y corre la simulación | `models`, `eventos`, `generador` |
| `gui/` | Todo lo visual (Streamlit) | `simulacion`, `models` |
| `app.py` | Arma la página, conecta los botones con el motor | `gui`, `simulacion` |

**Por qué importa esto para la defensa:** si te preguntan "¿por qué armaron
el proyecto así?", la respuesta es que así podés probar y entender la
simulación (con los tests de `tests/`) sin necesitar la interfaz, y pudimos
cambiar toda la GUI de PySide6 a Streamlit a mitad de proyecto sin tocar
una línea de `simulacion/`, `models/`, `eventos/` ni `generador/` — es la
prueba de que la separación funciona.

## 3. El generador de números aleatorios (`generador/`)

- `generador_congruencial.py`: implementa `Xₙ₊₁ = (a·Xₙ + c) mod m`, con los
  valores fijados por la consigna (semilla=1234, a=1714, c=1221, m=3922). El
  número U(0,1) es `Xₙ₊₁ / m`.
- **Un solo objeto `GeneradorCongruencial`** se crea en `MotorSimulacion` y
  se le pasa a las tres distribuciones (`dist_entre_llegadas_auto`,
  `dist_acreditacion`, `dist_permanencia_sala`). Cada vez que cualquiera de
  ellas pide un número, avanza la *misma* secuencia — así se cumple el
  requisito de "compartir el generador entre todas las variables".
- `distribucion_uniforme.py`: `valor = mínimo + R·(máximo − mínimo)`.
- `distribucion_exponencial.py`: método de la transformada inversa,
  `valor = −media · ln(1 − R)`.
- `integrador_euler.py`: integra `dD/dt` a pasos de tamaño `h` hasta que
  `D` alcanza el valor buscado. Se usa **solo** para la duración de la
  entrevista (no es aleatorio, es determinístico a partir de `P`).

**Pregunta típica: "¿por qué transformada inversa para la exponencial?"**
Porque es el método estándar para generar una variable aleatoria continua a
partir de un número uniforme, cuando se conoce la inversa de la función de
distribución acumulada (F⁻¹). Para la exponencial, esa inversa tiene forma
cerrada (`−media·ln(1−R)`), así que no hace falta aproximar nada.

## 4. Los objetos (`models/`)

- **`Invitado`** (objeto temporal): tiene `tipo` (con auto / peatón),
  `estado` (en qué etapa está) y timestamps de cada etapa por la que pasó.
  La propiedad `p` devuelve 100 o 70 según el tipo (se usa en la
  integración de Euler).
- **`Operario`** y **`Representante`** (objetos permanentes): representan
  los servidores de cada cola. `Operario` además acumula tiempo ocioso
  (para el objetivo 3 del TP).
- **`Cola`**: FIFO genérica reutilizada para acreditación y entrevista; la
  de entrevista tiene `tiempo_paciencia` para el abandono.
- **`FilaVectorEstado`**: una fila del vector de estado — todo lo que pide
  la consigna general (evento, próximos eventos, objetos con sus atributos,
  acumuladores, números aleatorios usados).

## 5. Los eventos (`eventos/`)

Son 7 tipos de evento (`TipoEvento`), uno por cada "cosa que puede pasar en
un instante":

1. `llegada_invitado_auto`
2. `fin_acreditacion`
3. `fin_estacionamiento`
4. `llegada_invitado_peaton`
5. `fin_permanencia_sala`
6. `fin_entrevista`
7. `abandono_entrevista`

`CalendarioEventos` es la lista de eventos futuros (FEL): un heap ordenado
por tiempo, así `proximo()` siempre devuelve el evento más cercano en el
tiempo en O(log n). La cancelación es "perezosa" (`cancelar` solo marca el
evento como cancelado; se descarta recién cuando le toca salir del heap) —
se usa para cancelar el abandono de un invitado que logra entrar a la
entrevista antes de los 5 minutos.

**Por qué no hay un evento `inicio_entrevista`:** empezar una entrevista es
una *reacción inmediata* dentro del manejo de otro evento (cuando termina
la permanencia en sala, o cuando se libera un representante), no algo que
se programa para el futuro. Solo se programan eventos cuyo instante no se
conoce hasta que ocurre otra cosa primero.

## 6. El motor de simulación (`simulacion/motor_simulacion.py`)

Es una simulación de **eventos discretos clásica** (next-event simulation):

```python
while True:
    si ya pedí que se detenga -> corto
    si llegué al máximo de iteraciones (N) -> corto
    evento = calendario.proximo()   # el más próximo en el tiempo
    si no hay más eventos -> corto
    si evento.tiempo > tiempo_max (X) -> corto
    reloj = evento.tiempo           # avanzo el reloj al evento
    proceso el evento (actualizo objetos, genero variables aleatorias,
                        programo nuevos eventos)
    agrego una fila al vector de estado
```

Cada tipo de evento tiene su propio método `_manejar_...`, registrado en un
diccionario (`_procesar_evento`) que hace de "switch". Cada manejador:

1. Actualiza el estado de los objetos involucrados (invitado, operario o
   representante).
2. Si corresponde, genera una variable aleatoria (y guarda el RND usado).
3. Programa el próximo evento relacionado.

El corte de la simulación (`motivo_corte`) puede ser por tres motivos:
tiempo máximo alcanzado, iteraciones máximas alcanzadas, o detenido a mano
— coincide con lo que pide la consigna ("lo que ocurra primero").

### Ejemplo para explicar paso a paso: un invitado con auto

1. `llegada_invitado_auto`: se crea el `Invitado`, se programa su próxima
   llegada (variable aleatoria Uniforme), y si hay un operario libre
   arranca la acreditación (genera el tiempo con la Exponencial).
2. `fin_acreditacion`: libera al operario, el invitado pasa a "estacionar"
   (3 min fijos), y si había alguien esperando en la cola, el mismo
   operario arranca con esa persona.
3. `fin_estacionamiento`: el invitado entra a la sala (genera su tiempo de
   permanencia con la Exponencial).
4. `fin_permanencia_sala`: el invitado pasa a la cola de entrevista. Si hay
   un representante libre, arranca la entrevista ahí mismo (integración de
   Euler para la duración); si no, espera y se programa su posible
   abandono a los 5 minutos.
5. `fin_entrevista` o `abandono_entrevista`: el invitado termina su paso
   por el sistema.

## 7. Qué es aleatorio y qué no (importante, preguntan esto seguido)

| Variable | ¿Aleatoria? | Distribución |
|---|---|---|
| Entre llegadas con auto | Sí | Uniforme(3, 7) |
| Tiempo de acreditación | Sí | Exponencial (media 2) |
| Permanencia en sala | Sí | Exponencial (media 20) |
| Entre llegadas peatón | No | Constante (2.5 min) |
| Tiempo de estacionar | No | Constante (3 min) |
| Duración de la entrevista | No | Determinística (integración de Euler de `dD/dt = P/5` hasta que `D` alcanza `P`) |

El criterio para decidir esto está en [SUPUESTOS.md](SUPUESTOS.md): el
enunciado da "+/-" o dice explícitamente "distribución exponencial negativa"
para las variables aleatorias; para las otras da un solo valor sin
distribución, así que se interpretan como constantes.

**Dato para lucirse:** como `dD/dt = P/5` es una tasa constante, la
integración siempre da `t = 5` unidades (50 minutos) sea `P=100` o `P=70` —
la duración de la entrevista termina siendo la misma para ambos tipos de
invitado. No es un error: es consecuencia de que el enunciado define una
ecuación lineal, y lo confirmó la docente por mail (está citado en
`SUPUESTOS.md`, punto 4).

## 8. Los tres objetivos de la simulación

1. **Máximo tiempo de permanencia en sala**: se actualiza en cada
   `fin_permanencia_sala`, comparando contra el máximo visto hasta ahora
   (`Acumuladores.registrar_tiempo_en_sala`).
2. **% de invitados que abandonan sin encuesta**: `cantidad_abandonos /
   cantidad_que_llegó_a_la_cola_de_entrevista × 100`.
3. **Tiempo ocioso promedio de los operarios**: cada `Operario` acumula su
   propio tiempo ocioso cada vez que pasa de libre a ocupado (compara el
   reloj actual contra la última vez que cambió de estado); al final de la
   simulación se cierra la cuenta para el tiempo ocioso que quedó abierto.

## 9. La interfaz (`gui/` + `app.py`)

- **Streamlit**, corre el script de Python de punta a punta en cada
  interacción (no es como una app de escritorio con eventos; cada click
  vuelve a ejecutar `app.py`). Por eso los resultados se guardan en
  `st.session_state` entre ejecuciones.
- La tabla del vector de estado y la de integración se arman como HTML
  propio (no con los componentes nativos de Streamlit) y se muestran con
  `st.iframe`: así el encabezado puede quedar anclado (`position: sticky`)
  de forma confiable, con su propio scroll, sin pelearse con el resto de
  la página.
- **Simular / Detener simulación**: la simulación corre en un hilo aparte
  (`threading.Thread`) para que el botón "Detener" pueda interrumpirla a
  mitad de camino (le pasa un `threading.Event` que el motor chequea en
  cada vuelta del `while`).

## 10. Preguntas que probablemente te hagan (y cómo responder)

- **"¿Por qué colas y no simplemente 'tiempo de espera'?"** → Porque hay un
  recurso limitado (3 operarios / 3 representantes): cuando todos están
  ocupados, el próximo invitado tiene que esperar en una cola FIFO.
- **"¿Cómo garantizan que el generador no se repite entre variables?"** →
  Es un único objeto compartido; cada llamada a `.siguiente()` avanza el
  mismo estado interno (`_x`), sin importar qué distribución lo llamó.
- **"¿Qué pasa si cambian la semilla?"** → Toda la secuencia de números
  cambia, pero el mecanismo es el mismo; es un parámetro de
  `ParametrosSimulacion`.
- **"¿Por qué el vector de estado no muestra TODOS los invitados en cada
  fila?"** → Porque la consigna pide no mostrar objetos que ya dejaron el
  sistema (retirados), salvo en la fila exacta en la que se retiran.
- **"¿Por qué el selector de invitados en la tabla de integración no
  tiene a todos?"** → Solo se calcula la integración para los invitados
  que llegaron a *empezar* la entrevista; la mayoría abandona antes
  (resultado consecuencia directa del modelo, con esta duración de
  entrevista tan larga frente a la demanda).
