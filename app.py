
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ==========================================
# 1. KONFIGURASI DASHBOARD
# ==========================================

st.set_page_config(
    page_title="Health Insight",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# 2. DESAIN DASAR
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7F8;
    }

    h1, h2, h3 {
        color: #173B43;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #E1E9EA;
    }

    section[data-testid="stSidebar"] {
        background-color: #E8F0EF;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. MEMBACA DATASET
# ==========================================

FILE_PATH = Path(__file__).parent / "health_data.xlsx"


@st.cache_data
def load_data():
    data = pd.read_excel(FILE_PATH)

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    return data


try:
    df = load_data()

except Exception as e:
    st.error(f"Gagal membaca dataset: {e}")
    st.stop()


# ==========================================
# 4. HEADER DASHBOARD
# ==========================================

st.title("🏥 HEALTH INSIGHT")
st.subheader("Health Outcomes Monitoring Dashboard")

st.markdown("""
Dashboard analisis kondisi kesehatan masyarakat berdasarkan
data rumah sakit, penyakit pernapasan, dan faktor cuaca.
""")

st.divider()


# ==========================================
# 5. SIDEBAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

hospitals = sorted(
    df["hospital_id"].dropna().unique()
)

selected_hospital = st.sidebar.selectbox(
    "Pilih Rumah Sakit",
    ["Semua Rumah Sakit"] + list(hospitals)
)

if df["date"].notna().any():

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    st.error("Kolom tanggal tidak memiliki data valid.")
    st.stop()


# ==========================================
# 6. FILTER DATA
# ==========================================

filtered_df = df.copy()

if selected_hospital != "Semua Rumah Sakit":

    filtered_df = filtered_df[
        filtered_df["hospital_id"] == selected_hospital
    ]

if (
    isinstance(selected_dates, (tuple, list))
    and len(selected_dates) == 2
):

    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["date"].dt.date >= start_date)
        & (filtered_df["date"].dt.date <= end_date)
    ]

if filtered_df.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()


# ==========================================
# 7. KPI UTAMA
# ==========================================

st.subheader("Health Overview")

total_respiratory = filtered_df["resp"].sum()
total_asthma = filtered_df["asthma_emegency_cases"].sum()
total_copd = filtered_df["copd_admissions"].sum()
total_death = filtered_df["death"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Kasus Pernapasan",
    f"{total_respiratory:,.0f}"
)

col2.metric(
    "Kasus Asma",
    f"{total_asthma:,.0f}"
)

col3.metric(
    "Kasus PPOK",
    f"{total_copd:,.0f}"
)

col4.metric(
    "Jumlah Kematian",
    f"{total_death:,.0f}"
)

st.divider()


# ==========================================
# 8. GRAFIK TREN KESEHATAN
# ==========================================

st.subheader("Health Trends")

daily_data = (
    filtered_df.groupby("date", as_index=False)[
        [
            "resp",
            "asthma_emegency_cases",
            "copd_admissions",
            "cvd"
        ]
    ]
    .sum()
)

daily_data = daily_data.melt(
    id_vars="date",
    var_name="Disease",
    value_name="Cases"
)

fig_trend = px.line(
    daily_data,
    x="date",
    y="Cases",
    color="Disease",
    markers=True,
    title="Daily Health Cases Trend",
    template="plotly_white"
)

fig_trend.update_layout(
    hovermode="x unified",
    legend_title="Health Category"
)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)


# ==========================================
# 9. PERBANDINGAN PENYAKIT
# ==========================================

st.subheader("Disease Comparison")

disease_data = pd.DataFrame({
    "Disease": [
        "Respiratory",
        "Asthma",
        "COPD",
        "Cardiovascular"
    ],
    "Cases": [
        filtered_df["resp"].sum(),
        filtered_df["asthma_emegency_cases"].sum(),
        filtered_df["copd_admissions"].sum(),
        filtered_df["cvd"].sum()
    ]
})

col_left, col_right = st.columns(2)

with col_left:

    fig_bar = px.bar(
        disease_data,
        x="Disease",
        y="Cases",
        color="Disease",
        title="Total Cases by Disease",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

with col_right:

    age_data = pd.DataFrame({
        "Age Group": [
            "Under 5 Years",
            "Over 60 Years"
        ],
        "Cases": [
            filtered_df["resp_admissions_under5"].sum(),
            filtered_df["resp_admissions_over60"].sum()
        ]
    })

    fig_age = px.pie(
        age_data,
        names="Age Group",
        values="Cases",
        hole=0.5,
        title="Respiratory Admissions by Age Group"
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )


# ==========================================
# 10. ANALISIS FAKTOR CUACA
# ==========================================

st.subheader("Weather Analysis")

col1, col2 = st.columns(2)

with col1:

    fig_temp = px.scatter(
        filtered_df,
        x="temp_c",
        y="resp",
        color="rhum_pct",
        title="Temperature vs Respiratory Cases",
        labels={
            "temp_c": "Temperature (°C)",
            "resp": "Respiratory Cases",
            "rhum_pct": "Humidity (%)"
        }
    )

    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )

with col2:

    fig_humidity = px.scatter(
        filtered_df,
        x="rhum_pct",
        y="resp",
        title="Humidity vs Respiratory Cases",
        labels={
            "rhum_pct": "Humidity (%)",
            "resp": "Respiratory Cases"
        }
    )

    st.plotly_chart(
        fig_humidity,
        use_container_width=True
    )


# ==========================================
# 11. TABEL DATA
# ==========================================

st.subheader("Health Data Explorer")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# 12. FOOTER
# ==========================================

st.divider()

st.caption(
    "HEALTH INSIGHT | Data-driven Public Health Monitoring"
)
