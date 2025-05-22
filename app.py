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

# --- Encabezado ---
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.image("https://raw.githubusercontent.com/1193-ai/analizador-financiero-streamlit/main/logo-temporal.png", width=100)
st.markdown("<h1>📊 Analiza tu estado</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Por Anny & Luis — Analiza estados financieros fácilmente.</p>", unsafe_allow_html=True)

# --- Subida de archivo ---
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx) con todos los estados financieros", type="xlsx")

def detectar_tipo_hoja(df):
    if "Concepto" not in df.columns:
        return None
    try:
        conceptos = df["Concepto"].astype(str).str.lower().tolist()
    except Exception:
        return None
    if any("activo" in c for c in conceptos) and any("pasivo" in c for c in conceptos):
        return "estado_situacion"
    elif any("ingresos" in c for c in conceptos) and any("gastos" in c for c in conceptos):
        return "estado_resultados"
    elif any("efectivo" in c for c in conceptos) and any("operación" in c for c in conceptos):
        return "flujo_efectivo"
    else:
        return None

def graficar_lineas(df, titulo):
    df_plot = df.set_index("Concepto").T
    fig, ax = plt.subplots()
    df_plot.plot(ax=ax)
    ax.set_title(titulo)
    st.pyplot(fig)

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.success(f"Archivo cargado con {len(xls.sheet_names)} hoja(s): {', '.join(xls.sheet_names)}")

    for hoja in xls.sheet_names:
        st.markdown(f"## 🗂️ Hoja: {hoja}")
        df = xls.parse(hoja)

        if df.columns[0].strip().lower() != "concepto":
            df = df.T
            df.columns = df.iloc[0]
            df = df[1:]
            df.reset_index(drop=True, inplace=True)
            df.insert(0, "Concepto", df.index)

        df = df.dropna(how="all")
        df = df.fillna(0)
        df.columns = df.columns.map(str)

        if "Concepto" not in df.columns:
            st.warning("⚠️ Esta hoja no tiene una columna llamada 'Concepto'.")
            continue

        tipo = detectar_tipo_hoja(df)

        if tipo == "estado_resultados":
            st.success("✅ Detectado: Estado de Resultados")
            df_numeric = df.set_index("Concepto").T
            df_numeric = df_numeric.apply(pd.to_numeric, errors='coerce')
            df_numeric.fillna(0, inplace=True)
            df_numeric["Margen de utilidad"] = (df_numeric["Ingresos"] - df_numeric["Gastos"]) / df_numeric["Ingresos"]

            st.subheader("📈 Margen de utilidad")
            st.line_chart(df_numeric[["Margen de utilidad"]])

            st.subheader("📊 Pastel de gastos vs ingresos último año")
            ultima = df_numeric.iloc[-1]
            fig, ax = plt.subplots()
            ax.pie([ultima["Gastos"], ultima["Ingresos"] - ultima["Gastos"]], labels=["Gastos", "Utilidad"], autopct="%1.1f%%")
            st.pyplot(fig)

        elif tipo == "estado_situacion":
            st.success("✅ Detectado: Estado de Situación Financiera")
            df_numeric = df.set_index("Concepto").T
            df_numeric = df_numeric.apply(pd.to_numeric, errors='coerce')
            df_numeric.fillna(0, inplace=True)
            df_numeric["Razón de endeudamiento"] = df_numeric["Pasivo Total"] / df_numeric["Activo Total"]

            st.subheader("📉 Razón de endeudamiento")
            st.bar_chart(df_numeric[["Razón de endeudamiento"]])

        elif tipo == "flujo_efectivo":
            st.success("✅ Detectado: Estado de Flujo de Efectivo")
            graficar_lineas(df, "Flujo de Efectivo por Actividad")

        else:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")
