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

# --- Funciones auxiliares ---

def estandarizar_columnas(cols):
    equivalencias = {
        "ingresos": "Ingresos",
        "gastos": "Gastos",
        "activo total": "Activo Total",
        "pasivo total": "Pasivo Total",
        "patrimonio": "Patrimonio",
        "utilidad neta": "Utilidad Neta",
        "flujo de efectivo": "Flujo de Efectivo",
        # Agrega más equivalencias si es necesario
    }
    return [equivalencias.get(col.lower().strip(), col) for col in cols]

def detectar_tipo_estado(df):
    cols = [str(c).lower() for c in df.columns]
    filas = [str(r).lower() for r in df.iloc[:,0]]

    # Detectar horizontal o vertical:
    es_horizontal = False
    es_vertical = False

    # Si hay columnas típicas en columnas -> horizontal
    if any(x in cols for x in ["ingresos", "gastos", "activo total", "pasivo total", "patrimonio"]):
        es_horizontal = True
    # Si hay filas típicas en la primera columna -> vertical
    elif any(x in filas for x in ["ingresos", "gastos", "activo total", "pasivo total", "patrimonio"]):
        es_vertical = True

    # Identificar tipo de estado financiero
    if es_horizontal:
        cols_lower = [c.lower() for c in df.columns]
        if "ingresos" in cols_lower and "gastos" in cols_lower:
            return "Estado de Resultados"
        elif "activo total" in cols_lower and "pasivo total" in cols_lower:
            return "Estado de Situación Financiera"
        elif "flujo de efectivo" in cols_lower or "flujo" in cols_lower:
            return "Estado de Flujo de Efectivo"
    elif es_vertical:
        filas_lower = [str(r).lower() for r in df.iloc[:,0]]
        if "ingresos" in filas_lower and "gastos" in filas_lower:
            return "Estado de Resultados"
        elif "activo total" in filas_lower and "pasivo total" in filas_lower:
            return "Estado de Situación Financiera"
        elif "flujo de efectivo" in filas_lower or "flujo" in filas_lower:
            return "Estado de Flujo de Efectivo"

    return None

def preparar_df(df):
    # Detectar orientación
    cols = [str(c).lower() for c in df.columns]
    filas = [str(r).lower() for r in df.iloc[:,0]]

    if any(x in cols for x in ["ingresos", "gastos", "activo total", "pasivo total", "patrimonio"]):
        # Horizontal: estandarizar columnas
        df.columns = estandarizar_columnas(df.columns)
        df = df.dropna(how='all')  # eliminar filas vacías
        df = df.dropna(axis=1, how='all')  # eliminar columnas vacías
        df = df.reset_index(drop=True)
    elif any(x in filas for x in ["ingresos", "gastos", "activo total", "pasivo total", "patrimonio"]):
        # Vertical: convertir primera columna a índices, luego transponer
        df.columns = [str(c) for c in df.columns]
        df = df.set_index(df.columns[0]).T
        df.columns = estandarizar_columnas(df.columns)
        df = df.reset_index(drop=True)
    else:
        # No identificado
        pass

    # Convertir todas las columnas a numéricas donde sea posible (salvo la primera si quedó índice)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# --- Carga y análisis ---

uploaded_file = st.file_uploader("📁 Sube tu archivo Excel (.xlsx) con todos los estados financieros", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.success(f"Archivo cargado con {len(xls.sheet_names)} hoja(s): {', '.join(xls.sheet_names)}")
    
    for hoja in xls.sheet_names:
        st.markdown(f"---\n## Hoja: {hoja}")
        df_raw = pd.read_excel(xls, hoja)
        
        tipo = detectar_tipo_estado(df_raw)
        if not tipo:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")
            continue

        st.write(f"**Tipo detectado:** {tipo}")

        df = preparar_df(df_raw)
        st.subheader("📄 Datos cargados:")
        st.dataframe(df)

        # Cálculo de ratios comunes (solo para Resultados y Situación Financiera)
        if tipo == "Estado de Resultados" or tipo == "Estado de Situación Financiera":
            # Añadir columnas calculadas solo si existen las necesarias
            if all(col in df.columns for col in ["Ingresos", "Gastos"]):
                df["Margen de utilidad"] = (df["Ingresos"] - df["Gastos"]) / df["Ingresos"]
            if all(col in df.columns for col in ["Ingresos", "Gastos", "Activo Total"]):
                df["ROA"] = (df["Ingresos"] - df["Gastos"]) / df["Activo Total"]
            if all(col in df.columns for col in ["Ingresos", "Gastos", "Patrimonio"]):
                df["ROE"] = (df["Ingresos"] - df["Gastos"]) / df["Patrimonio"]
            if all(col in df.columns for col in ["Pasivo Total", "Activo Total"]):
                df["Razón de endeudamiento"] = df["Pasivo Total"] / df["Activo Total"]

            # Mostrar ratios calculados (solo si existen)
            cols_ratios = [c for c in ["Margen de utilidad", "ROA", "ROE", "Razón de endeudamiento"] if c in df.columns]
            if cols_ratios:
                st.subheader("📈 Ratios financieros:")
                st.write(df[cols_ratios])

        # Interpretación
        st.subheader("🧠 Interpretación automática:")

        for index, row in df.iterrows():
            st.markdown(f"### 📅 Periodo {index + 1}")

            # Interpretación de Margen de utilidad
            if "Margen de utilidad" in df.columns and not pd.isna(row["Margen de utilidad"]):
                margen = row["Margen de utilidad"]
                if margen > 0.2:
                    st.write(f"✅ Margen de utilidad del {margen:.2%}: Excelente rentabilidad.")
                elif margen > 0.1:
                    st.write(f"🟡 Margen de utilidad del {margen:.2%}: Rentabilidad aceptable.")
                else:
                    st.write(f"🔴 Margen de utilidad del {margen:.2%}: Rentabilidad baja o crítica.")

            # Interpretación de ROA
            if "ROA" in df.columns and not pd.isna(row["ROA"]):
                roa = row["ROA"]
                if roa > 0.15:
                    st.write(f"✅ ROA del {roa:.2%}: Alta eficiencia del uso de activos.")
                elif roa > 0.05:
                    st.write(f"🟡 ROA del {roa:.2%}: Eficiencia moderada.")
                else:
                    st.write(f"🔴 ROA del {roa:.2%}: Baja eficiencia en activos.")

            # Interpretación de ROE
            if "ROE" in df.columns and not pd.isna(row["ROE"]):
                roe = row["ROE"]
                if roe > 0.15:
                    st.write(f"✅ ROE del {roe:.2%}: Buen retorno al accionista.")
                elif roe > 0.05:
                    st.write(f"🟡 ROE del {roe:.2%}: Retorno moderado.")
                else:
                    st.write(f"🔴 ROE del {roe:.2%}: Bajo retorno, debe revisarse.")

            # Interpretación de razón de endeudamiento
            if "Razón de endeudamiento" in df.columns and not pd.isna(row["Razón de endeudamiento"]):
                endeudamiento = row["Razón de endeudamiento"]
                if endeudamiento < 0.4:
                    st.write(f"✅ Razón de endeudamiento baja ({endeudamiento:.2f}): Buena salud financiera.")
                elif endeudamiento < 0.7:
                    st.write(f"🟡 Razón de endeudamiento moderada ({endeudamiento:.2f}): Cuidado con el endeudamiento.")
                else:
                    st.write(f"🔴 Razón de endeudamiento alta ({endeudamiento:.2f}): Riesgo financiero alto.")

        # Gráficos
        st.subheader("📊 Gráficos:")

        if tipo == "Estado de Resultados":
            if "Margen de utilidad" in df.columns:
                fig, ax = plt.subplots()
                ax.plot(df.index, df["Margen de utilidad"], marker='o', linestyle='-', color='#1e90ff')
                ax.set_title("Margen de utilidad por periodo")
                ax.set_xlabel("Periodo")
                ax.set_ylabel("Margen de utilidad")
                ax.grid(True)
                st.pyplot(fig)

        elif tipo == "Estado de Situación Financiera":
            # Gráfico de barras para Activo, Pasivo y Patrimonio si existen
            cols_barras = []
            for c in ["Activo Total", "Pasivo Total", "Patrimonio"]:
                if c in df.columns:
                    cols_barras.append(c)
            if cols_barras:
                fig2, ax2 = plt.subplots()
                df[cols_barras].plot(kind='bar', ax=ax2, color=['#4caf50', '#f44336', '#2196f3'])
                ax2.set_title("Activo, Pasivo y Patrimonio por periodo")
                ax2.set_xlabel("Periodo")
                ax2.set_ylabel("Monto")
                ax2.legend(loc='upper right')
                st.pyplot(fig2)

            # Gráfico de pastel para estructura financiera (Pasivo vs Patrimonio)
            try:
                pasivo_total = pd.to_numeric(df["Pasivo Total"]).sum()
                patrimonio = pd.to_numeric(df["Patrimonio"]).sum()
                activo_total = pd.to_numeric(df["Activo Total"]).sum()

                if activo_total > 0:
                    valores = [pasivo_total, patrimonio]
                    etiquetas = ["Pasivo Total", "Patrimonio"]
                    colores = ["#ff9999", "#66b3ff"]

                    fig3, ax3 = plt.subplots()
                    ax3.pie(valores, labels=etiquetas, colors=colores, autopct='%1.1f%%', startangle=140)
                    ax3.axis('equal')
                    ax3.set_title("Distribución Pasivo y Patrimonio sobre Activo Total")
                    st.pyplot(fig3)
                else:
                    st.warning("El Activo Total es cero o inválido, no se puede mostrar gráfico de pastel.")
            except Exception as e:
                st.error(f"No se pudo crear gráfico de pastel: {e}")

        elif tipo == "Estado de Flujo de Efectivo":
            # Simple gráfica de barras del flujo de efectivo si existe
            if "Flujo de Efectivo" in df.columns:
                fig4, ax4 = plt.subplots()
                df["Flujo de Efectivo"].plot(kind='bar', ax=ax4, color='#ffa726')
                ax4.set_title("Flujo de efectivo por periodo")
                ax4.set_xlabel("Periodo")
                ax4.set_ylabel("Monto")
                st.pyplot(fig4)
            else:
                st.info("No se encontraron datos para gráfico de flujo de efectivo.")

st.markdown("</div>", unsafe_allow_html=True)
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
    conceptos = df['Concepto'].str.lower().tolist()
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

def mostrar_variaciones(df):
    # Asumimos que 'Concepto' es la primera columna y los demás son años o períodos
    df_numeric = df.set_index("Concepto").apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Calcular variaciones porcentuales año a año
    variaciones = df_numeric.pct_change(axis=1) * 100
    variaciones = variaciones.round(2).fillna(0)
    
    # Preparar un DataFrame para mostrar con símbolos de cambio
    variaciones_simbolos = variaciones.copy().astype(str)
    
    for col in variaciones.columns:
        variaciones_simbolos[col] = variaciones[col].apply(
            lambda x: f"{x}% 📈" if x > 5 else (f"{x}% 📉" if x < -5 else f"{x}% ⚠️")
        )
    
    st.subheader("📊 Variaciones año a año (%)")
    st.dataframe(variaciones_simbolos)

    # Mostrar tabla con valores y variaciones lado a lado
    valores_y_variaciones = pd.concat([df_numeric, variaciones_simbolos], keys=["Valores", "Variaciones"], axis=1)
    st.subheader("📋 Valores y variaciones combinadas")
    st.dataframe(valores_y_variaciones)

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    st.success(f"Archivo cargado con {len(xls.sheet_names)} hoja(s): {', '.join(xls.sheet_names)}")

    for hoja in xls.sheet_names:
        st.markdown(f"## 🗂️ Hoja: {hoja}")
        df = xls.parse(hoja)

        if df.columns[0].lower() != "concepto":
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

            # Mostrar variaciones año a año
            mostrar_variaciones(df)

        elif tipo == "estado_situacion":
            st.success("✅ Detectado: Estado de Situación Financiera")
            df_numeric = df.set_index("Concepto").T
            df_numeric = df_numeric.apply(pd.to_numeric, errors='coerce')
            df_numeric.fillna(0, inplace=True)
            df_numeric["Razón de endeudamiento"] = df_numeric["Pasivo Total"] / df_numeric["Activo Total"]

            st.subheader("📉 Razón de endeudamiento")
            st.bar_chart(df_numeric[["Razón de endeudamiento"]])

            # Mostrar variaciones año a año
            mostrar_variaciones(df)

        elif tipo == "flujo_efectivo":
            st.success("✅ Detectado: Estado de Flujo de Efectivo")
            graficar_lineas(df, "Flujo de Efectivo por Actividad")

            # Mostrar variaciones año a año
            mostrar_variaciones(df)

        else:
            st.warning("⚠️ No se pudo determinar el tipo de estado financiero para esta hoja.")

st.markdown("</div>", unsafe_allow_html=True)
