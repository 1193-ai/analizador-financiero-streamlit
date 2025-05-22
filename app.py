import streamlit as st
import pandas as pd

st.title("📊 Analizador Financiero")
st.write("Sube un archivo de Excel con tu estado financiero:")

uploaded_file = st.file_uploader("📁 Subir archivo .xlsx", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("📋 Vista previa de los datos")
    st.dataframe(df)

    try:
        # Cálculos básicos
        df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]
        df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
        df["Rentabilidad del patrimonio"] = (df["Ingresos"] - df["Gastos"]) / df["Patrimonio"]

        st.subheader("📈 Ratios financieros calculados")
        st.dataframe(df[["Razón de endeudamiento", "Margen de utilidad", "Rentabilidad del patrimonio"]])

        st.subheader("📊 Gráfica de margen de utilidad")
        st.line_chart(df["Margen de utilidad"])
    except Exception as e:
        st.error(f"❌ Error al calcular ratios: {e}")
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
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.subheader("📄 Datos cargados:")
    st.dataframe(df)

    # Cálculo de ratios
    st.subheader("📈 Ratios financieros:")

    df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
    df["ROA"] = (df["Ingresos"] - df["Gastos"]) / df["Activo Total"]
    df["ROE"] = (df["Ingresos"] - df["Gastos"]) / df["Patrimonio"]
    df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]

    st.write(df[["Margen de utilidad", "ROA", "ROE", "Razón de endeudamiento"]])

    # Gráfico
    st.subheader("📊 Gráfico de margen de utilidad:")
    fig, ax = plt.subplots()
    df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
    ax.set_ylabel("Margen")
    ax.set_xlabel("Periodo")
    st.pyplot(fig)

st.markdown("</div>", unsafe_allow_html=True)
