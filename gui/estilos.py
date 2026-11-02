"""Estilos visuales de la interfaz (solo apariencia, nada de lógica de simulación).

Adaptado del TP3 del mismo grupo para mantener la misma estética entre
trabajos prácticos.
"""
import streamlit as st

MARINO = "#0b2545"
AZUL = "#1d5fbf"
CELESTE = "#3b9fdc"
INDIGO = "#6a5acd"
NEUTRO = "#a9b8cc"
TEXTO = "#10233f"
TEXTO_SUAVE = "#4a5f7d"
FONDO_TARJETA = "#ffffff"
FONDO_AVISO = "#e8f3fc"
BORDE = "#c8d6ea"

CSS = f"""
<style>
.hero {{ background: linear-gradient(120deg, {MARINO} 0%, {AZUL} 100%); color: #ffffff;
  border-radius: 14px; padding: 22px 28px; margin-bottom: 18px; }}
.hero-etiqueta {{ color: #cfe4fa; font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; }}
.hero-titulo {{ color: #ffffff; font-size: 1.9rem; font-weight: 700; margin: 4px 0 6px; line-height: 1.2; }}
.hero-sub {{ color: #dbeafb; font-size: .95rem; }}
.hero-chips {{ margin-top: 12px; display: flex; flex-wrap: wrap; gap: 8px; }}
.hero-chip {{ background: rgba(255,255,255,.14); color: #ffffff; border: 1px solid rgba(255,255,255,.35);
  border-radius: 999px; padding: 3px 12px; font-size: .8rem; }}

[class*="st-key-caja"] {{ background: {FONDO_TARJETA}; border-radius: 12px !important;
  box-shadow: 0 1px 3px rgba(11,37,69,.08); }}
/* El tema oscuro de Streamlit pone texto claro por defecto (p, td, th, li, etc.);
   como forzamos fondo blanco en las tarjetas, hay que forzar también el color de
   letra, o queda texto claro sobre blanco (ilegible). */
[class*="st-key-caja"] p,
[class*="st-key-caja"] span,
[class*="st-key-caja"] li,
[class*="st-key-caja"] td,
[class*="st-key-caja"] th,
[class*="st-key-caja"] label {{ color: {TEXTO} !important; }}
/* Los botones (Simular, Exportar a Excel, etc.) tienen fondo oscuro propio,
   así que necesitan texto claro — la regla de arriba los oscurecía también. */
[class*="st-key-caja"] button p,
[class*="st-key-caja"] button span {{ color: #ffffff !important; }}
/* Alinea el botón con los number_input de al lado: estos tienen una etiqueta
   arriba (label + margen) que el botón no tiene, así que hay que compensar
   con margin-top, y además el botón es por defecto un poco más alto. */
[class*="st-key-boton_exportar"] {{ margin-top: 30px; }}
[class*="st-key-boton_exportar"] button {{ background-color: #1a8a4a !important;
  border-color: #1a8a4a !important; height: 36px !important; min-height: 36px !important;
  padding-top: 0 !important; padding-bottom: 0 !important;
  box-sizing: border-box; display: flex; align-items: center; justify-content: center; }}
[class*="st-key-boton_exportar"] button:hover {{ background-color: #157a40 !important;
  border-color: #157a40 !important; }}
/* La barra se separa del texto en un elemento propio de alto fijo, para que
   no crezca junto con el título cuando este ocupa más de una línea. */
.titulo-seccion {{ display: flex; align-items: stretch; gap: 12px; margin-bottom: 6px; }}
.titulo-seccion .barra {{ width: 4px; min-height: 28px; align-self: flex-start;
  background: {AZUL}; border-radius: 2px; flex-shrink: 0; }}
.titulo-seccion .numero {{ color: {AZUL}; }}
.titulo-seccion .titulo {{ color: {MARINO}; font-size: 1.25rem; font-weight: 700; line-height: 1.3; }}
.titulo-seccion .subtitulo {{ color: {TEXTO_SUAVE}; font-size: .88rem; margin-top: 2px; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 6px 0 12px; }}
.kpi {{ background: #f7faff; color: {TEXTO}; border: 1px solid {BORDE}; border-top: 3px solid {AZUL};
  border-radius: 10px; padding: 10px 14px; }}
.kpi-label {{ color: {TEXTO_SUAVE}; font-size: .74rem; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }}
.kpi-valor {{ color: {MARINO}; font-size: 1.55rem; font-weight: 700; margin-top: 2px; line-height: 1.2; }}
.kpi-unidad {{ color: {TEXTO_SUAVE}; font-size: .9rem; font-weight: 600; margin-left: 3px; }}
.kpi-detalle {{ color: {TEXTO_SUAVE}; font-size: .78rem; margin-top: 2px; }}

.aviso {{ background: {FONDO_AVISO}; color: {TEXTO}; border-left: 4px solid {AZUL};
  border-radius: 8px; padding: 10px 14px; margin: 6px 0 10px; font-size: .95rem; }}
.aviso b {{ color: {MARINO}; }}
</style>
"""


def inyectar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def html(contenido, destino=st):
    destino.markdown(contenido, unsafe_allow_html=True)


def encabezado_app(titulo, subtitulo):
    html(f'<div class="hero"><div class="hero-etiqueta">UTN FRC · Simulación · TP5 · Grupo 6</div>'
         f'<div class="hero-titulo">{titulo}</div><div class="hero-sub">{subtitulo}</div></div>')


def titulo_seccion(titulo, subtitulo=None, numero=None, destino=st):
    numero_html = f'<span class="numero">{numero}. </span>' if numero is not None else ""
    sub_html = f'<div class="subtitulo">{subtitulo}</div>' if subtitulo else ""
    html(
        f'<div class="titulo-seccion"><span class="barra"></span>'
        f'<div><div class="titulo">{numero_html}{titulo}</div>{sub_html}</div></div>',
        destino,
    )


def seccion(clave, titulo, subtitulo=None, numero=None, altura=None):
    """Recuadro blanco con borde y título. Se usa con:  with seccion(...):

    `altura` (px) fuerza una altura fija para toda la tarjeta (título
    incluido) — útil para que dos tarjetas lado a lado queden del mismo
    alto. El contenido que no entre en esa altura debe manejar su propio
    scroll interno (ver `renderizar_tabla_integracion`), para que el
    título nunca se desplace.
    """
    kwargs = {"height": altura} if altura is not None else {}
    caja = st.container(border=True, key=f"caja_{clave}", **kwargs)
    titulo_seccion(titulo, subtitulo, numero, destino=caja)
    return caja


def tarjetas_kpi(indicadores, destino=st):
    """indicadores: lista de (etiqueta, valor, unidad, detalle)."""
    tarjetas = "".join(
        f'<div class="kpi"><div class="kpi-label">{etiqueta}</div>'
        f'<div class="kpi-valor">{valor}<span class="kpi-unidad">{unidad}</span></div>'
        f'<div class="kpi-detalle">{detalle}</div></div>'
        for etiqueta, valor, unidad, detalle in indicadores)
    html(f'<div class="kpi-grid">{tarjetas}</div>', destino)


def aviso(texto, destino=st):
    html(f'<div class="aviso">{texto}</div>', destino)
