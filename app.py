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

def estandarizar_columnas(columnas):
    equivalencias = {
        "ingresos": "Ingresos",
        "gastos": "Gastos",
        "activo total": "Activo Total",
        "pasivo total": "Pasivo Total",
        "patrimonio": "Patrimonio",
        "utilidad neta": "Utilidad Neta",
        "flujo neto de efectivo": "Flujo Neto de Efectivo",
        # agrega más equivalencias si quieres
    }
    return [equivalencias.get(col.lower().strip(), col) for col in columnas]

def determinar_tipo_estado(df):
    cols = [c.lower() for c in df.columns]
    rows = [str(r).lower() for r in df.iloc[:, 0]]

    # Intento detectar estado de resultados
    if "ingresos" in cols or "gastos" in cols or "utilidad neta" in cols or "utilidad" in cols:
        return "Estado de Resultados"
    if "activo total" in cols or "pasivo total" in cols or "patrimonio" in cols:
        return "Estado de Situación Financiera"
    if "flujo neto de efectivo" in cols or "flujo de efectivo" in cols:
        return "Estado de Flujo de Efectivo"

    # Verifico filas si la info está vertical
    if any("ingresos" in r for r in rows) or any("gastos" in r for r in rows):
        return "Estado de Resultados"
    if any("activo total" in r for r in rows) or any("pasivo total" in r for r in rows) or any("patrimonio" in r for r in rows):
        return "Estado de Situación Financiera"
    if any("flujo neto de efectivo" in r for r in rows) or any("flujo de efectivo" in r for r in rows):
        return "Estado de Flujo de Efectivo"

    return None

def interpretar_margen(margen):
    if pd.isnull(margen):
        return "Datos insuficientes para interpretar margen."
    if margen > 0.2:
        return f"✅ Margen de utilidad del {margen:.2%}: Excelente rentabilidad."
    elif margen > 0.1:
        return f"🟡 Margen de utilidad del {margen:.2%}: Rentabilidad aceptable."
    else:
        return f"🔴 Margen de utilidad del {margen:.2%}: Rentabilidad baja o crítica."

def interpretar_roa(roa):
    if pd.isnull(roa):
        return "Datos insuficientes para interpretar ROA."
    if roa > 0.15:
        return f"✅ ROA del {roa:.2%}: Alta eficiencia del uso de activos."
    elif roa > 0.05:
        return f"🟡 ROA del {roa:.2%}: Eficiencia moderada."
    else:
        return f"🔴 ROA del {roa:.2%}: Baja eficiencia en activos."

def interpretar_roe(roe):
    if pd.isnull(roe):
        return "Datos insuficientes para interpretar ROE."
    if roe > 0.15:
        return f"✅ ROE del {roe:.2%}: Buen retorno al accionista."
    elif roe > 0.05:
        return f"🟡 ROE del {roe:.2%}: Retorno moderado."
    else:
        return f"🔴 ROE del {roe:.2%}: Bajo retorno, debe revisarse."

def interpretar_deuda(deuda):
    if pd.isnull(deuda):
        return "Datos insuficientes para interpretar razón de endeudamiento."
    if deuda < 0.4:
        return f"✅ Razón de endeudamiento del {deuda:.2%}: Bajo riesgo financiero."
    elif deuda < 0.7:
        return f"🟡 Razón de endeudamiento del {deuda:.2%}: Nivel manejable."
    else:
        return f"🔴 Razón de endeudamiento del {deuda:.2%}: Riesgo alto de deuda."

# --- Encabezado ---
st.markdown("<div class='main'>", unsafe_allow_html=True)
st.image("https://raw.githubusercontent.com/1193-ai/analizador-financiero-streamlit/main/logo-temporal.png", width=100)
st.markdown("<h1>📊 Analiza tu estado</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo'>Por Anny & Luis — Analiza estados financieros fácilmente.</p>", unsafe_allow_html=True)

# --- Subida de archivo ---
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx) con hojas múltiples", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.write(f"🗂️ Hojas detectadas: {xls.sheet_names}")

    for hoja in xls.sheet_names:
        st.markdown(f"## 📄 Hoja: {hoja}")
        df = pd.read_excel(xls, hoja)

        # Detectar si está vertical (filas) o horizontal (columnas)
        tipo = determinar_tipo_estado(df)

        if tipo is None:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")
            continue

        st.write(f"**Tipo detectado:** {tipo}")

        # Si está vertical (columnas genéricas, datos en filas), trasponer para estandarizar
        # Verificamos si en columnas no están las palabras clave pero sí en filas
        columnas_lower = [c.lower() for c in df.columns]
        filas_lower = [str(r).lower() for r in df.iloc[:, 0]]

        if tipo == "Estado de Resultados" and not ("ingresos" in columnas_lower or "gastos" in columnas_lower):
            df = df.T
            df.columns = df.iloc[0]
            df = df.drop(df.index[0])
            df = df.reset_index(drop=True)
            df.columns = estandarizar_columnas(df.columns)
        elif tipo == "Estado de Situación Financiera" and not ("activo total" in columnas_lower or "pasivo total" in columnas_lower):
            df = df.T
            df.columns = df.iloc[0]
            df = df.drop(df.index[0])
            df = df.reset_index(drop=True)
            df.columns = estandarizar_columnas(df.columns)
        elif tipo == "Estado de Flujo de Efectivo" and not ("flujo neto de efectivo" in columnas_lower):
            df = df.T
            df.columns = df.iloc[0]
            df = df.drop(df.index[0])
            df = df.reset_index(drop=True)
            df.columns = estandarizar_columnas(df.columns)
        else:
            # Ya están en formato horizontal con columnas bien nombradas
            df.columns = estandarizar_columnas(df.columns)

        st.subheader("📄 Datos cargados:")
        st.dataframe(df)

        if tipo == "Estado de Resultados":
            # Calcular ratios
            try:
                df["Margen de utilidad"] = (pd.to_numeric(df["Ingresos"]) - pd.to_numeric(df["Gastos"])) / pd.to_numeric(df["Ingresos"])
                df["ROA"] = (pd.to_numeric(df["Ingresos"]) - pd.to_numeric(df["Gastos"])) / pd.to_numeric(df["Activo Total"])
                df["ROE"] = (pd.to_numeric(df["Ingresos"]) - pd.to_numeric(df["Gastos"])) / pd.to_numeric(df["Patrimonio"])
                df["Razón de endeudamiento"] = pd.to_numeric(df["Pasivo Total"]) / pd.to_numeric(df["Activo Total"])
            except Exception as e:
                st.error(f"Error calculando ratios: {e}")
                continue

            st.subheader("📈 Ratios financieros:")
            st.write(df[["Margen de utilidad", "ROA", "ROE", "Razón de endeudamiento"]])

            st.subheader("🧠 Interpretación automática:")
            for i, row in df.iterrows():
                margen = row.get("Margen de utilidad", None)
                roa = row.get("ROA", None)
                roe = row.get("ROE", None)
                deuda = row.get("Razón de endeudamiento", None)

                st.markdown(f"### 📅 Periodo {i + 1}")
                st.write(interpretar_margen(margen))
                st.write(interpretar_roa(roa))
                st.write(interpretar_roe(roe))
                st.write(interpretar_deuda(deuda))
                st.markdown("---")

            # Gráfica
            st.subheader("📊 Gráfica Margen de utilidad:")
            plt.figure(figsize=(8, 4))
            plt.plot(df.index, df["Margen de utilidad"], marker='o')
            plt.title("Margen de utilidad por periodo")
            plt.xlabel("Periodo")
            plt.ylabel("Margen de utilidad")
            plt.grid(True)
            st.pyplot(plt)

        elif tipo == "Estado de Situación Financiera":
            st.write("Aquí puedes agregar análisis específicos para este estado.")

        elif tipo == "Estado de Flujo de Efectivo":
            st.write("Aquí puedes agregar análisis específicos para flujo de efectivo.")

st.markdown("</div>", unsafe_allow_html=True)

