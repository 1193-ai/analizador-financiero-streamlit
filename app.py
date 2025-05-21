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
