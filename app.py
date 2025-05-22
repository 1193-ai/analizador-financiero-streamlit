import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Configuración de página ---
st.set_page_config(page_title="Analiza tu estado", page_icon="📊", layout="centered")

# --- Estilo personalizado ---
st.markdown("""
    <style>
        body {
            background-color: #f0f8ff;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
        }
        h1 {
            color: #1e90ff;
        }
        .subtitulo {
            font-size: 18px;
            color: #444;
        }
    </style>
""", unsafe_allow_html=True)

# --- Función para estandarizar columnas con seguridad ---
def estandarizar_columnas(columnas):
    equivalencias = {
        "ingresos": "Ingresos",
        "ventas": "Ingresos",
        "gastos": "Gastos",
        "costos": "Gastos",
        "activo total": "Activo Total",
        "total activo": "Activo Total",
        "pasivo total": "Pasivo Total",
        "total pasivo": "Pasivo Total",
        "patrimonio": "Patrimonio",
        "capital": "Patrimonio",
        "flujo de efectivo": "Flujo de Efectivo",
        "estado de resultados": "Estado de Resultados",
        "estado de situacion financiera": "Estado de Situación Financiera"
    }
    columnas_limpias = []
    for col in columnas:
        if col is None:
            columnas_limpias.append(col)
            continue
        try:
            c = str(col).lower().strip()
        except Exception:
            c = str(col)
        columnas_limpias.append(equivalencias.get(c, col))
    return columnas_limpias

# --- Función para detectar tipo de estado financiero ---
def detectar_tipo_estado(df):
    # Revisar columnas (horizontal)
    cols = [str(c).lower() for c in df.columns if c is not None]
    # Revisar filas (vertical)
    filas = [str(f).lower() for f in df.iloc[:,0] if f is not None]

    claves_situacion = {"activo total", "pasivo total", "patrimonio"}
    claves_resultados = {"ingresos", "ventas", "gastos", "costos"}
    claves_flujo = {"flujo de efectivo", "actividades de operación", "actividades de inversión", "actividades de financiamiento"}

    # Detectar en columnas
    if any(clave in cols for clave in claves_situacion):
        return "Situación Financiera", "horizontal"
    if any(clave in cols for clave in claves_resultados):
        return "Estado de Resultados", "horizontal"
    if any(clave in cols for clave in claves_flujo):
        return "Flujo de Efectivo", "horizontal"

    # Detectar en filas (primera columna)
    if any(clave in filas for clave in claves_situacion):
        return "Situación Financiera", "vertical"
    if any(clave in filas for clave in claves_resultados):
        return "Estado de Resultados", "vertical"
    if any(clave in filas for clave in claves_flujo):
        return "Flujo de Efectivo", "vertical"

    return None, None

# --- Función para transformar vertical a horizontal ---
def vertical_a_horizontal(df):
    df_clean = df.dropna(how="all").reset_index(drop=True)
    df_clean = df_clean.rename(columns={df_clean.columns[0]: "Indicador"})
    df_clean = df_clean.set_index("Indicador").T.reset_index(drop=True)
    # Reemplazamos nombres si hay
    df_clean.columns.name = None
    return df_clean

# --- Función para analizar y mostrar ratios e interpretaciones ---
def analizar_estado(df, tipo):

    st.subheader(f"📄 Datos procesados del {tipo}:")
    st.dataframe(df)

    if tipo == "Situación Financiera" or tipo == "Estado de Resultados":
        # Intentamos estandarizar columnas
        df.columns = estandarizar_columnas(df.columns)

    # Cálculos para situación financiera y resultados
    if tipo == "Estado de Resultados":
        # Asumimos columnas: Ingresos, Gastos
        if all(x in df.columns for x in ["Ingresos", "Gastos"]):
            df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
            st.subheader("📈 Margen de utilidad:")
            st.write(df["Margen de utilidad"])

            # Gráfico
            fig, ax = plt.subplots()
            df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
            ax.set_ylabel("Margen")
            ax.set_xlabel("Periodo")
            st.pyplot(fig)

            # Interpretación
            st.subheader("🧠 Interpretación automática:")
            for i, row in df.iterrows():
                margen = row["Margen de utilidad"]
                if margen > 0.2:
                    st.write(f"✅ Margen de utilidad del {margen:.2%}: Excelente rentabilidad.")
                elif margen > 0.1:
                    st.write(f"🟡 Margen de utilidad del {margen:.2%}: Rentabilidad aceptable.")
                else:
                    st.write(f"🔴 Margen de utilidad del {margen:.2%}: Rentabilidad baja o crítica.")
                st.markdown("---")
        else:
            st.warning("No se encontraron las columnas necesarias para calcular el margen de utilidad (Ingresos y Gastos).")

    elif tipo == "Situación Financiera":
        # Asumimos columnas: Activo Total, Pasivo Total, Patrimonio
        if all(x in df.columns for x in ["Activo Total", "Pasivo Total", "Patrimonio"]):
            df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]
            st.subheader("📈 Razón de endeudamiento:")
            st.write(df["Razón de endeudamiento"])

            # Gráfico
            fig, ax = plt.subplots()
            df["Razón de endeudamiento"].plot(kind="bar", ax=ax, color="#1e90ff")
            ax.set_ylabel("Razón")
            ax.set_xlabel("Periodo")
            st.pyplot(fig)

            # Interpretación
            st.subheader("🧠 Interpretación automática:")
            for i, row in df.iterrows():
                deuda = row["Razón de endeudamiento"]
                if deuda < 0.4:
                    st.write(f"✅ Razón de endeudamiento del {deuda:.2%}: Bajo riesgo financiero.")
                elif deuda < 0.7:
                    st.write(f"🟡 Razón de endeudamiento del {deuda:.2%}: Nivel manejable.")
                else:
                    st.write(f"🔴 Razón de endeudamiento del {deuda:.2%}: Riesgo alto de deuda.")
                st.markdown("---")
        else:
            st.warning("No se encontraron las columnas necesarias para calcular razón de endeudamiento (Activo Total, Pasivo Total, Patrimonio).")

    elif tipo == "Flujo de Efectivo":
        # Aquí puedes poner análisis específicos para flujo de efectivo
        st.write("📊 Datos del Flujo de Efectivo (sin análisis específico aún):")
        st.dataframe(df)
    else:
        st.warning("No se pudo determinar el análisis para este tipo de estado financiero.")

# --- App principal ---
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.image("https://raw.githubusercontent.com/1193-ai/analizador-financiero-streamlit/main/logo-temporal.png", width=100)
st.markdown("<h1>📊 Analiza tu estado</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Por Anny & Luis — Analiza estados financieros fácilmente.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx) con varios estados financieros", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.write(f"Este archivo tiene {len(xls.sheet_names)} hojas: {xls.sheet_names}")

    for hoja in xls.sheet_names:
        st.markdown(f"---\n### Hoja: {hoja}")
        df = xls.parse(hoja)

        # Detectar formato y tipo
        tipo, formato = detectar_tipo_estado(df)
        if tipo is None:
            st.warning(f"⚠️ No se pudo determinar el tipo de estado financiero para la hoja '{hoja}'.")
            continue

        if formato == "vertical":
            df = vertical_a_horizontal(df)

        analizar_estado(df, tipo)

st.markdown("</div>", unsafe_allow_html=True)

