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

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx) con todos los estados financieros", type="xlsx")

def detectar_tipo_estado(df):
    texto_completo = ' '.join([str(c).lower() for c in df.columns]) + ' ' + ' '.join([str(i).lower() for i in df.index])

    if any(keyword in texto_completo for keyword in ["activo", "pasivo", "patrimonio", "situación financiera"]):
        return "situacion"
    elif any(keyword in texto_completo for keyword in ["ingresos", "ventas", "utilidad", "ganancia", "resultado neto"]):
        return "resultados"
    elif any(keyword in texto_completo for keyword in ["efectivo", "flujo", "actividades operativas", "inversión", "financiación"]):
        return "flujo"
    else:
        return None

def procesar_estado_resultados(df):
    try:
        df = df.fillna(0)
        st.subheader("📈 Ratios financieros del Estado de Resultados")
        df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
        st.dataframe(df[["Ingresos", "Gastos", "Margen de utilidad"]])

        st.subheader("📊 Gráfico de margen de utilidad")
        fig, ax = plt.subplots()
        df["Margen de utilidad"].plot(kind="bar", ax=ax, color="#1e90ff")
        ax.set_ylabel("Margen")
        ax.set_xlabel("Periodo")
        st.pyplot(fig)

        st.subheader("🧠 Interpretaciones")
        for i, row in df.iterrows():
            margen = row["Margen de utilidad"]
            if margen > 0.2:
                st.write(f"✅ Periodo {i}: Margen excelente ({margen:.2%})")
            elif margen > 0.1:
                st.write(f"🟡 Periodo {i}: Margen aceptable ({margen:.2%})")
            else:
                st.write(f"🔴 Periodo {i}: Margen bajo ({margen:.2%})")
        st.markdown("---")
    except Exception as e:
        st.error("Error procesando Estado de Resultados: " + str(e))

def procesar_estado_situacion(df):
    try:
        df = df.fillna(0)
        st.subheader("📈 Ratios del Estado de Situación Financiera")
        df["ROA"] = (df["Ingresos"] - df["Gastos"]) / df["Activo Total"]
        df["ROE"] = (df["Ingresos"] - df["Gastos"]) / df["Patrimonio"]
        df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]
        st.dataframe(df[["ROA", "ROE", "Razón de endeudamiento"]])

        st.subheader("🧠 Interpretaciones")
        for i, row in df.iterrows():
            roa = row["ROA"]
            roe = row["ROE"]
            deuda = row["Razón de endeudamiento"]

            st.write(f"### 📅 Periodo {i}")
            if roa > 0.15:
                st.write(f"✅ ROA alto ({roa:.2%})")
            elif roa > 0.05:
                st.write(f"🟡 ROA moderado ({roa:.2%})")
            else:
                st.write(f"🔴 ROA bajo ({roa:.2%})")

            if roe > 0.15:
                st.write(f"✅ ROE fuerte ({roe:.2%})")
            elif roe > 0.05:
                st.write(f"🟡 ROE aceptable ({roe:.2%})")
            else:
                st.write(f"🔴 ROE bajo ({roe:.2%})")

            if deuda < 0.4:
                st.write(f"✅ Endeudamiento bajo ({deuda:.2%})")
            elif deuda < 0.7:
                st.write(f"🟡 Nivel de deuda razonable ({deuda:.2%})")
            else:
                st.write(f"🔴 Endeudamiento alto ({deuda:.2%})")
        st.markdown("---")
    except Exception as e:
        st.error("Error procesando Estado de Situación Financiera: " + str(e))

def procesar_estado_flujo(df):
    try:
        df = df.fillna(0)
        st.subheader("📈 Análisis del Flujo de Efectivo")
        df["Flujo neto"] = df.sum(axis=1)
        st.dataframe(df[["Flujo neto"]])

        st.subheader("📊 Gráfico del Flujo de Efectivo")
        fig, ax = plt.subplots()
        df["Flujo neto"].plot(kind="line", ax=ax, marker='o', color="#ff6347")
        ax.set_ylabel("Flujo neto")
        ax.set_xlabel("Periodo")
        st.pyplot(fig)

        st.subheader("🧠 Interpretación")
        for i, row in df.iterrows():
            flujo = row["Flujo neto"]
            if flujo > 0:
                st.write(f"✅ Periodo {i}: Flujo positivo ({flujo})")
            elif flujo == 0:
                st.write(f"🟡 Periodo {i}: Flujo neutro ({flujo})")
            else:
                st.write(f"🔴 Periodo {i}: Flujo negativo ({flujo})")
        st.markdown("---")
    except Exception as e:
        st.error("Error procesando Flujo de Efectivo: " + str(e))

if uploaded_file:
    hojas_excel = pd.read_excel(uploaded_file, sheet_name=None)
    st.success(f"Archivo cargado con {len(hojas_excel)} hoja(s): {', '.join(hojas_excel.keys())}")

    for nombre_hoja, df in hojas_excel.items():
        st.markdown(f"## 📄 Hoja: {nombre_hoja}")

        if df.shape[0] < df.shape[1]:
            df = df.transpose()

        tipo = detectar_tipo_estado(df)

        if tipo == "situacion":
            procesar_estado_situacion(df)
        elif tipo == "resultados":
            procesar_estado_resultados(df)
        elif tipo == "flujo":
            procesar_estado_flujo(df)
        else:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")
