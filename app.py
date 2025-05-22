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

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel con múltiples hojas (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        st.success("Archivo cargado correctamente. Se encontraron las siguientes hojas:")
        st.write(xls.sheet_names)

        for sheet_name in xls.sheet_names:
            st.markdown(f"## 📄 Hoja: {sheet_name}")
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Transponer si los datos están en vertical
            if df.columns[0] in ["Ingresos", "Ventas", "Gastos", "Activo Total"]:
                df.set_index(df.columns[0], inplace=True)
                df = df.transpose().reset_index(drop=True)

            elif df.iloc[0, 0] in ["Ingresos", "Ventas", "Gastos", "Activo Total"]:
                df = df.set_index(df.columns[0]).transpose().reset_index(drop=True)

            st.dataframe(df)

            required_cols = ["Ingresos", "Gastos", "Activo Total", "Pasivo Total", "Patrimonio"]
            if all(col in df.columns for col in required_cols):
                st.subheader("📈 Ratios financieros:")
                df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
                df["ROA"] = (df["Ingresos"] - df["Gastos"]) / df["Activo Total"]
                df["ROE"] = (df["Ingresos"] - df["Gastos"]) / df["Patrimonio"]
                df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]

                st.write(df[["Margen de utilidad", "ROA", "ROE", "Razón de endeudamiento"]])

                st.subheader("🧠 Interpretación automática:")

                for index, row in df.iterrows():
                    st.markdown(f"### 📅 Periodo {index + 1}")
                    margen = row["Margen de utilidad"]
                    roa = row["ROA"]
                    roe = row["ROE"]
                    deuda = row["Razón de endeudamiento"]

                    # Interpretaciones
                    if margen > 0.2:
                        st.write(f"✅ Margen de utilidad del {margen:.2%}: Excelente rentabilidad.")
                    elif margen > 0.1:
                        st.write(f"🟡 Margen de utilidad del {margen:.2%}: Rentabilidad aceptable.")
                    else:
                        st.write(f"🔴 Margen de utilidad del {margen:.2%}: Rentabilidad baja o crítica.")

                    if roa > 0.15:
                        st.write(f"✅ ROA del {roa:.2%}: Alta eficiencia del uso de activos.")
                    elif roa > 0.05:
                        st.write(f"🟡 ROA del {roa:.2%}: Eficiencia moderada.")
                    else:
                        st.write(f"🔴 ROA del {roa:.2%}: Baja eficiencia en activos.")

                    if roe > 0.15:
                        st.write(f"✅ ROE del {roe:.2%}: Buen retorno al accionista.")
                    elif roe > 0.05:
                        st.write(f"🟡 ROE del {roe:.2%}: Retorno moderado.")
                    else:
                        st.write(f"🔴 ROE del {roe:.2%}: Bajo retorno, debe revisarse.")

                    if deuda < 0.4:
                        st.write(f"✅ Razón de endeudamiento del {deuda:.2%}: Bajo riesgo financiero.")
                    elif deuda < 0.7:
                        st.write(f"🟡 Razón de endeudamiento del {deuda:.2%}: Nivel manejable.")
                    else:
                        st.write(f"🔴 Razón de endeudamiento del {deuda:.2%}: Riesgo alto de deuda.")
                    st.markdown("---")

                # Gráfico
                st.subheader("📊 Gráfico de margen de utilidad:")
                fig, ax = plt.subplots()
                df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
                ax.set_ylabel("Margen")
                ax.set_xlabel("Periodo")
                st.pyplot(fig)

            else:
                st.info("Esta hoja no contiene los datos necesarios para calcular los ratios financieros.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")

