import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analiza tu estado", page_icon="📊", layout="centered")

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

st.markdown("<div class='main'>", unsafe_allow_html=True)
st.image("https://raw.githubusercontent.com/1193-ai/analizador-financiero-streamlit/main/logo-temporal.png", width=100)
st.markdown("<h1>📊 Analiza tu estado</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Por Anny & Luis — Analiza estados financieros fácilmente.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx)", type="xlsx")

# Sinónimos para ayudar a identificar los estados financieros
def estandarizar_columnas(columnas):
    equivalencias = {
        "ventas": "Ingresos",
        "ventas netas": "Ingresos",
        "ingresos operacionales": "Ingresos",
        "egresos": "Gastos",
        "costos": "Gastos",
        "activo total": "Activo Total",
        "total activo": "Activo Total",
        "pasivo total": "Pasivo Total",
        "total pasivo": "Pasivo Total",
        "patrimonio neto": "Patrimonio",
        "capital contable": "Patrimonio"
    }
    return [equivalencias.get(col.lower().strip(), col) for col in columnas]

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    for nombre_hoja in xls.sheet_names:
        st.markdown(f"## 📄 Hoja: {nombre_hoja}")
        df = pd.read_excel(xls, sheet_name=nombre_hoja)

        if df.columns[0] != "Periodo":
            df = df.set_index(df.columns[0]).T.reset_index(drop=True)

        df.columns = estandarizar_columnas(df.columns)

        columnas = df.columns.str.lower()

        if "ingresos" in columnas and "gastos" in columnas:
            tipo = "Estado de Resultados"
        elif "activo total" in columnas and "pasivo total" in columnas and "patrimonio" in columnas:
            tipo = "Estado de Situación Financiera"
        elif any("operación" in col for col in columnas) or any("flujo" in col for col in columnas):
            tipo = "Estado de Flujo de Efectivo"
        else:
            tipo = None

        if tipo:
            st.markdown(f"**Tipo de estado detectado:** {tipo}")
            st.dataframe(df)

            if tipo == "Estado de Resultados" or tipo == "Estado de Situación Financiera":
                if "Ingresos" in df.columns and "Gastos" in df.columns:
                    df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
                    df["ROA"] = (df["Ingresos"] - df["Gastos"]) / df.get("Activo Total", 1)
                    df["ROE"] = (df["Ingresos"] - df["Gastos"]) / df.get("Patrimonio", 1)

                if "Pasivo Total" in df.columns and "Activo Total" in df.columns:
                    df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]

                st.subheader("📈 Ratios financieros:")
                ratios_cols = [col for col in ["Margen de utilidad", "ROA", "ROE", "Razón de endeudamiento"] if col in df.columns]
                st.write(df[ratios_cols])

                st.subheader("🧠 Interpretación automática:")
                for index, row in df.iterrows():
                    st.markdown(f"### 📅 Periodo {index + 1}")
                    margen = row.get("Margen de utilidad")
                    roa = row.get("ROA")
                    roe = row.get("ROE")
                    deuda = row.get("Razón de endeudamiento")

                    if margen is not None:
                        if margen > 0.2:
                            st.write(f"✅ Margen de utilidad del {margen:.2%}: Excelente rentabilidad.")
                        elif margen > 0.1:
                            st.write(f"🟡 Margen de utilidad del {margen:.2%}: Rentabilidad aceptable.")
                        else:
                            st.write(f"🔴 Margen de utilidad del {margen:.2%}: Rentabilidad baja o crítica.")

                    if roa is not None:
                        if roa > 0.15:
                            st.write(f"✅ ROA del {roa:.2%}: Alta eficiencia del uso de activos.")
                        elif roa > 0.05:
                            st.write(f"🟡 ROA del {roa:.2%}: Eficiencia moderada.")
                        else:
                            st.write(f"🔴 ROA del {roa:.2%}: Baja eficiencia en activos.")

                    if roe is not None:
                        if roe > 0.15:
                            st.write(f"✅ ROE del {roe:.2%}: Buen retorno al accionista.")
                        elif roe > 0.05:
                            st.write(f"🟡 ROE del {roe:.2%}: Retorno moderado.")
                        else:
                            st.write(f"🔴 ROE del {roe:.2%}: Bajo retorno, debe revisarse.")

                    if deuda is not None:
                        if deuda < 0.4:
                            st.write(f"✅ Razón de endeudamiento del {deuda:.2%}: Bajo riesgo financiero.")
                        elif deuda < 0.7:
                            st.write(f"🟡 Razón de endeudamiento del {deuda:.2%}: Nivel manejable.")
                        else:
                            st.write(f"🔴 Razón de endeudamiento del {deuda:.2%}: Riesgo alto de deuda.")

                    st.markdown("---")

                if "Margen de utilidad" in df.columns:
                    st.subheader("📊 Gráfico de margen de utilidad:")
                    fig, ax = plt.subplots()
                    df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
                    ax.set_ylabel("Margen")
                    ax.set_xlabel("Periodo")
                    st.pyplot(fig)
        else:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")
