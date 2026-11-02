# TP5 Simulación — Degustación (Grupo 6)

Simulación de eventos discretos de una degustación de embutidos y vinos: cola
de acreditación en el portón (3 operarios) y cola de entrevista de
satisfacción (3 representantes), con GUI en Streamlit.

## 1. Requisitos

- Python 3.11 (recomendado — ver nota abajo sobre versiones más nuevas).
- macOS/Linux/Windows con terminal.

> **Nota:** se probó que Python 3.14 (muy reciente) da problemas de
> inicialización con algunas librerías de interfaz gráfica en este entorno.
> Si tenés varias versiones de Python instaladas, usá 3.11 para crear el
> entorno virtual del proyecto.

## 2. Preparar el entorno (una sola vez)

Parado en la carpeta del proyecto:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

En Windows (PowerShell), el segundo paso es `.venv\Scripts\Activate.ps1`.

## 3. Ejecutar la aplicación

Con el entorno activado:

```bash
source .venv/bin/activate
streamlit run app.py
```

Se abre automáticamente en el navegador en `http://localhost:8501`. Si no se
abre solo, entrá a esa dirección manualmente.

Para volver a correrla en otra sesión de terminal, solo hace falta repetir
los dos comandos de arriba (activar el entorno y `streamlit run app.py`) —
no hace falta reinstalar nada.

### Si editás el código mientras la app está corriendo

Streamlit detecta los cambios en los archivos y muestra un aviso arriba a la
derecha ("Source file changed") con un botón **Rerun**. Hay que apretarlo
(o la tecla `R`) para que la app tome el código nuevo — no se actualiza sola.

## 4. Usar la aplicación

1. En la barra lateral, ajustá los parámetros que necesites (todos tienen el
   valor por defecto del enunciado).
2. Apretá **Simular**. Mientras corre, los parámetros quedan bloqueados.
3. Mirá los resultados en **"1. Resultados de la simulación"** y la
   integración de Euler en **"3. Integración numérica"**.
4. En **"2. Vector de estado"** podés elegir desde qué hora mostrar filas y
   cuántas, y exportar todo a Excel con el botón verde.
5. Apretá **Detener simulación** para desbloquear los parámetros y poder
   correr una simulación nueva (también sirve para cortar una simulación muy
   larga antes de que termine sola).

## 5. Correr los tests

```bash
source .venv/bin/activate
python -m pytest -q
```

Hay 15 tests que cubren el generador congruencial, las distribuciones
(uniforme y exponencial), la integración de Euler y la cola FIFO.

## 6. Estructura del proyecto

```
app.py                  # Punto de entrada de la app (Streamlit)
models/                 # Objetos del sistema: Invitado, Operario, Representante, Cola, FilaVectorEstado
eventos/                 # Evento, TipoEvento, CalendarioEventos (lista de eventos futuros)
generador/               # Generador congruencial + distribuciones + integrador de Euler
simulacion/              # Motor de simulación, parámetros, acumuladores
gui/                      # Todo lo visual (Streamlit): estilos, tablas, panel de parámetros
tests/                    # Tests del generador, distribuciones, integrador y cola
SUPUESTOS.md             # Decisiones de diseño y ambigüedades resueltas del enunciado
GUIA_DEFENSA.md          # Guía para explicar/defender el código (ver abajo)
```

Para más detalle de cada módulo y cómo explicarlo en la defensa, ver
[GUIA_DEFENSA.md](GUIA_DEFENSA.md). Para las decisiones de modelado (qué
colas hay, qué es aleatorio y qué no, etc.), ver [SUPUESTOS.md](SUPUESTOS.md).
