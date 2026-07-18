import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio

st.set_page_config(
    page_title="US Manufacturing Energy 2022 Classification: NAICS Classification",
    layout="wide",
)

pio.templates.default = "plotly"

SHEET_NAME = "Process-level data"
DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD4/main/WebsiteEngine3.xlsx"

NAICS_COLORS = [
    "#0F4C5C", "#7A1F1F", "#5C4D7D", "#8A5A00",
    "#006D5B", "#8C2F39", "#355C7D", "#6B3E26",
    "#1D3557", "#7F5539", "#6A040F", "#3A5A40",
]

PROCESS_COLORS = [
    "#7A1F5C", "#A23B72", "#5B2A86", "#8C1C13",
    "#6C584C", "#2D6A4F", "#8D5524", "#3D405B",
    "#7B2CBF", "#9C6644", "#6F1D1B", "#386641",
]

ENERGY_SOURCE_COLORS = {
    "Annual Fuels": "#C05A00",
    "Annual Steam": "#355C9A",
    "Annual Electricity": "#1F8A4C",
}

TEMP_COLORS = {
    "<20 °C": "#2A9D8F",
    "20-100 °C": "#7FBF7B",
    "100-200 °C": "#B9770E",
    "200-400 °C": "#C0392B",
    "400-600 °C": "#8E5EA2",
    ">=600 °C": "#5B2C6F",
}

def norm(x):
    return " ".join(
        str(x).replace("\n", " ").replace("(", "").replace(")", "").strip().split()
    ).lower()

def pick_col(df, target):
    matches = [c for c in df.columns if norm(c) == norm(target)]
    return matches[0] if matches else None

def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def fmt_pj(x):
    return f"{x:,.2f}"

def style_donut(fig):
    fig.update_traces(
        domain=dict(x=[0.00, 0.72]),
        textinfo="percent",
        hovertemplate="%{label}<br>%{value:,.2f} PJ<br>%{percent}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(t=60, b=20, l=20, r=20),
        legend=dict(
            x=0.75,
            y=0.5,
            xanchor="left",
            yanchor="middle",
            font=dict(size=12),
        ),
    )
    return fig

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_URL, sheet_name=SHEET_NAME, header=1, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > 0:
        first_row = " ".join([str(x) for x in df.iloc[0].fillna("").tolist()])
        if "GJ/FU" in first_row or "PJ" in first_row or "bara" in first_row:
            df = df.iloc[1:].copy()

    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    return df

df = load_data()

naics_l1_col = pick_col(df, "NAICS Level 1")
naics_l2_col = pick_col(df, "NAICS Level 2")
industrial_process_col = pick_col(df, "Industrial process")
percent_energy_col = pick_col(df, "Percent Annual energy demand in 2022")
temperature_col = pick_col(df, "Process Temperature for Webpage")
total_energy_col = pick_col(df, "Annual energy demand in 2022")
electricity_col = pick_col(df, "Annual electricity demand in 2022")
fuels_col = pick_col(df, "Annual fuels demand in 2022")
steam_col = pick_col(df, "Annual fuels or electricity for steam or steam from CHP demand in 2022")
percent_coverage_col = pick_col(df, "Percent Coverage of NAICS 3-digit Sector")

required = {
    "NAICS Level 1": naics_l1_col,
    "NAICS Level 2": naics_l2_col,
    "Industrial process": industrial_process_col,
    "Percent Annual energy demand in 2022": percent_energy_col,
    "Process Temperature for Webpage": temperature_col,
    "Annual energy demand in 2022": total_energy_col,
    "Annual electricity demand in 2022": electricity_col,
    "Annual fuels demand in 2022": fuels_col,
    "Steam demand": steam_col,
    "Percent Coverage": percent_coverage_col,
}

missing = [k for k, v in required.items() if v is None]

st.title("2022 U.S. Manufacturing Energy Consumption by NAICS Classification")

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_options = sorted(df[naics_l1_col].dropna().astype(str).drop_duplicates().tolist())

if not naics_options:
    st.error("No NAICS Level 1 values found.")
    st.stop()

selected_naics = st.selectbox(
    "Select a NAICS code to view its energy use breakdown",
    naics_options,
    index=0,
)

df_filtered = df[df[naics_l1_col].astype(str) == str(selected_naics)].copy()

total_energy = num(df_filtered[total_energy_col]).sum()
total_electricity = num(df_filtered[electricity_col]).sum()
total_fuels = num(df_filtered[fuels_col]).sum()
total_steam = num(df_filtered[steam_col]).sum()
percent_coverage = num(df_filtered[percent_coverage_col]).sum()
percent_coverage_text = f"{percent_coverage:.2%}" if percent_coverage > 0 else "N/A"

st.markdown(f"""
<div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem;">
    <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Total annual energy<br><b>{fmt_pj(total_energy)} PJ</b></div>
    <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual electricity<br><b>{fmt_pj(total_electricity)} PJ</b></div>
    <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual fuels<br><b>{fmt_pj(total_fuels)} PJ</b></div>
    <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual steam<br><b>{fmt_pj(total_steam)} PJ</b></div>
    <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Database coverage<br><b>{percent_coverage_text}</b></div>
</div>
""", unsafe_allow_html=True)

breakdown_df = pd.DataFrame({
    "Type": ["Fuels", "Steam", "Electricity"],
    "Value": [total_fuels, total_steam, total_electricity],
})
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

naics_donut_df = (
    df_filtered[[naics_l2_col, total_energy_col]]
    .assign(**{total_energy_col: pd.to_numeric(df_filtered[total_energy_col], errors="coerce")})
    .dropna(subset=[naics_l2_col, total_energy_col])
    .groupby(naics_l2_col, as_index=False)[total_energy_col]
    .sum()
    .rename(columns={naics_l2_col: "NAICS Level 2", total_energy_col: "Annual Energy"})
)
naics_donut_df = naics_donut_df[naics_donut_df["Annual Energy"] > 0].sort_values("Annual Energy", ascending=False)

process_df = (
    df_filtered[[industrial_process_col, total_energy_col]]
    .assign(**{total_energy_col: pd.to_numeric(df_filtered[total_energy_col], errors="coerce")})
    .dropna(subset=[industrial_process_col, total_energy_col])
    .groupby(industrial_process_col, as_index=False)[total_energy_col]
    .sum()
    .rename(columns={industrial_process_col: "Industrial process", total_energy_col: "Annual Energy"})
)
process_df = process_df[process_df["Annual Energy"] > 0].sort_values("Annual Energy", ascending=False)

temp_df = df_filtered[[temperature_col, total_energy_col]].copy()
temp_df.columns = ["Temperature", "Annual Energy"]
temp_df["Temperature"] = pd.to_numeric(temp_df["Temperature"], errors="coerce")
temp_df["Annual Energy"] = pd.to_numeric(temp_df["Annual Energy"], errors="coerce")
temp_df = temp_df.dropna(subset=["Temperature"])
temp_df = temp_df[temp_df["Annual Energy"] > 0].copy()

temp_df["Temperature Range"] = pd.cut(
    temp_df["Temperature"],
    bins=[-float("inf"), 20, 100, 200, 400, 600, float("inf")],
    labels=[
        "<20 °C",
        "20-100 °C",
        "100-200 °C",
        "200-400 °C",
        "400-600 °C",
        ">=600 °C",
    ],
    right=False,
)

temp_donut_df = (
    temp_df.dropna(subset=["Temperature Range"])
    .groupby("Temperature Range", as_index=False)["Annual Energy"]
    .sum()
)
temp_donut_df = temp_donut_df[temp_donut_df["Annual Energy"] > 0].copy()

col1, col2 = st.columns(2)

with col1:
    if not naics_donut_df.empty:
        fig = px.pie(
            naics_donut_df,
            names="NAICS Level 2",
            values="Annual Energy",
            hole=0.62,
            color="NAICS Level 2",
            color_discrete_sequence=NAICS_COLORS,
            title="NAICS Subsectors Within",
        )
        fig = style_donut(fig)
        st.plotly_chart(fig, use_container_width=True)

    if not process_df.empty:
        fig = px.pie(
            process_df,
            names="Industrial process",
            values="Annual Energy",
            hole=0.62,
            color="Industrial process",
            color_discrete_sequence=PROCESS_COLORS,
            title="Industrial Processes Within",
        )
        fig = style_donut(fig)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if not breakdown_df.empty:
        fig = px.pie(
            breakdown_df,
            names="Type",
            values="Value",
            hole=0.62,
            color="Type",
            color_discrete_map=ENERGY_SOURCE_COLORS,
            title="Distribution by Energy Source",
        )
        fig = style_donut(fig)
        st.plotly_chart(fig, use_container_width=True)

    if not temp_donut_df.empty:
        fig = px.pie(
            temp_donut_df,
            names="Temperature Range",
            values="Annual Energy",
            hole=0.62,
            color="Temperature Range",
            color_discrete_map=TEMP_COLORS,
            category_orders={
        "Temperature Range": [
            "<20 °C",
            "20-100 °C",
            "100-200 °C",
            "200-400 °C",
            "400-600 °C",
            ">=600 °C",
        ]
    },
    title="Distribution by Process Temperature",
        )
        fig = style_donut(fig)
        st.plotly_chart(fig, use_container_width=True)
