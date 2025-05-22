import streamlit as st
import pandas as pd
impo
rt matplotlib.pyplot as plt

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
    excel_data = pd.read_excel(uploaded_file, sheet_name=None)

    for sheet_name, df in excel_data.items():
        st.markdown(f"## 📄 Hoja: {sheet_name}")
        df = df.dropna(how='all').dropna(axis=1, how='all')  # Limpieza básica

        # Detectar si los datos están en columnas o filas
        if df.columns[0] not in ["Ingresos", "Ventas", "Activo Total"]:
            df = df.set_index(df.columns[0]).T.reset_index(drop=True)

        df.columns = [str(c).strip() for c in df.columns]  # Quitar espacios

        st.subheader("📄 Datos cargados:")
        st.dataframe(df)

        # Detectar tipo de estado financiero
        columnas = df.columns

        if "Ingresos" in columnas and "Gastos" in columnas:
            st.subheader("📈 Ratios financieros - Estado de Resultados:")
            df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
            st.write(df[["Margen de utilidad"]])

            st.subheader("📊 Gráfico de margen de utilidad:")
            fig, ax = plt.subplots()
            df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
            ax.set_ylabel("Margen")
            ax.set_xlabel("Periodo")
            st.pyplot(fig)

        elif "Activo Total" in columnas and "Pasivo Total" in columnas and "Patrimonio" in columnas:
            st.subheader("📈 Ratios financieros - Estado de Situación Financiera:")
            df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]
            df["ROE"] = (df.get("Utilidad Neta", 0)) / df["Patrimonio"]
            st.write(df[["Razón de endeudamiento", "ROE"]])

        elif "Flujo de operación" in columnas and "Flujo de inversión" in columnas and "Flujo de financiamiento" in columnas:
            st.subheader("📈 Flujos - Estado de Flujo de Efectivo:")
            df["Flujo neto"] = df["Flujo de operación"] + df["Flujo de inversión"] + df["Flujo de financiamiento"]
            st.write(df[["Flujo neto"]])

            st.subheader("📊 Gráfico de flujo neto:")
            fig, ax = plt.subplots()
            df["Flujo neto"].plot(kind="bar", ax=ax, color="#32cd32")
            ax.set_ylabel("Flujo neto")
            ax.set_xlabel("Periodo")
            st.pyplot(fig)

        else:
            st.warning("No se pudo determinar el tipo de estado financiero para esta hoja.")

        st.markdown("---")
