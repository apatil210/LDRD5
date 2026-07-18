import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="US Manufacturing Energy Classification: Unit Operations", layout="wide")

SHEET_NAME = "Process-level data"
GITHUB_URL = "https://github.com/apatil210/LDRD2/raw/main/Modified%20Data%20for%20NAICS.xlsx"
LOCAL_FILE = "Modified-Data-for-NAICS.xlsx"

EXPECTED = {
    "naics_l1": "NAICS Level 1",
    "naics_l2": "NAICS Level 2",
    "industrial_process": "Industrial process",
    "coverage": "Percent Coverage of NAICS (3-digit) Sector",
    "annual_energy": "Annual energy demand in 2022",
    "annual_electricity": "Annual electricity demand in 2022",
    "annual_fuels": "Annual fuels demand in 2022",
    "annual_steam": "Annual fuels or electricity for steam or steam from CHP demand in 2022",
}

def norm(x):
    return " ".join(str(x).replace("\n", " ").strip().split()).lower()

@st.cache_data
def load_data():
    source = LOCAL_FILE if Path(LOCAL_FILE).exists() else GITHUB_URL
    df = pd.read_excel(source, sheet_name=SHEET_NAME, header=1)
    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > 0:
        first_row = " ".join([str(x) for x in df.iloc[0].fillna("").tolist()])
        if "GJ/FU" in first_row or "PJ" in first_row or "bara" in first_row:
            df = df.iloc[1:].copy()

    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    return df

def resolve_columns(df):
    norm_map = {norm(c): c for c in df.columns}
    resolved, missing = {}, []

    for k, expected in EXPECTED.items():
        found = norm_map.get(norm(expected))
        if found is None:
            for c in df.columns:
                cn = norm(c)
                if k == "coverage" and "percent coverage of naics" in cn and "sector" in cn:
                    found = c
                    break
                if k == "naics_l2" and cn.startswith("naics level 2"):
                    found = c
                    break
                if k == "naics_l1" and cn.startswith("naics level 1"):
                    found = c
                    break
                if k == "industrial_process" and "industrial process" in cn:
                    found = c
                    break
                if k == "annual_energy" and cn.startswith("annual energy demand in 2022"):
                    found = c
                    break
                if k == "annual_electricity" and cn.startswith("annual electricity demand in 2022"):
                    found = c
                    break
                if k == "annual_fuels" and cn.startswith("annual fuels demand in 2022"):
                    found = c
                    break
                if k == "annual_steam" and "annual fuels or electricity for steam" in cn and "demand in 2022" in cn:
                    found = c
                    break

        if found is None:
            missing.append(expected)
        else:
            resolved[k] = found

    return resolved, missing

def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)

def fmt_pj(x):
    return f"{x:,.2f} PJ"

df = load_data()
cols, missing = resolve_columns(df)

st.markdown(
    """
    <style>
    .stApp {
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }
    h1, h2, h3 {
        color: #1e293b !important;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.92rem;
        color: #64748b;
        margin-bottom: 0.15rem;
    }
    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
    }
    .coverage-label {
        margin-top: 0.35rem;
        margin-bottom: 1rem;
        font-size: 0.98rem;
        color: #0f172a;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1>US Manufacturing Energy Classification: NAICS</h1>", unsafe_allow_html=True)
st.write("Select a NAICS Level (3-digit code) sector to generate an energy fact sheet.")

if missing:
    st.error("Missing required columns: " + ", ".join(missing))
    st.write("Available columns:", list(df.columns))
    st.stop()

naics_l1_col = cols["naics_l1"]
naics_l2_col = cols["naics_l2"]
industrial_process_col = cols["industrial_process"]
coverage_col = cols["coverage"]
annual_energy_col = cols["annual_energy"]
annual_electricity_col = cols["annual_electricity"]
annual_fuels_col = cols["annual_fuels"]
annual_steam_col = cols["annual_steam"]

naics_options = sorted(df[naics_l1_col].dropna().astype(str).drop_duplicates().tolist())
selected_naics = st.selectbox("NAICS Level 1", naics_options, index=0)

df_filtered = df[df[naics_l1_col].astype(str) == str(selected_naics)].copy()

coverage_values = pd.to_numeric(df_filtered[coverage_col], errors="coerce").dropna()
coverage = coverage_values.sum() if not coverage_values.empty else None
coverage_text = f"{coverage:.2%}" if coverage is not None else "N/A"

st.markdown(
    f'<div class="coverage-label">Total Sector Coverage of {selected_naics}: {coverage_text}</div>',
    unsafe_allow_html=True,
)

total_energy = num(df_filtered[annual_energy_col]).sum()
total_electricity = num(df_filtered[annual_electricity_col]).sum()
total_fuels = num(df_filtered[annual_fuels_col]).sum()
total_steam = num(df_filtered[annual_steam_col]).sum()

m1, m2, m3, m4 = st.columns(4)
for col, label, value in [
    (m1, "Total annual energy", total_energy),
    (m2, "Annual electricity", total_electricity),
    (m3, "Annual fuels", total_fuels),
    (m4, "Annual steam", total_steam),
]:
    with col:
        st.markdown(
            f'<div class="card"><div class="metric-label">{label}</div><div class="metric-value">{fmt_pj(value)}</div></div>',
            unsafe_allow_html=True,
        )

breakdown_df = pd.DataFrame(
    {
        "Type": ["Annual Fuels", "Annual Steam", "Annual Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    }
)
breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

bar_df = df_filtered[[naics_l2_col, annual_energy_col]].copy()
bar_df[annual_energy_col] = pd.to_numeric(bar_df[annual_energy_col], errors="coerce")
bar_df = (
    bar_df.dropna(subset=[naics_l2_col, annual_energy_col])
    .groupby(naics_l2_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={naics_l2_col: "NAICS Level 2", annual_energy_col: "Annual Energy"})
)
bar_df = bar_df[bar_df["Annual Energy"] > 0].copy()

process_df = df_filtered[[industrial_process_col, annual_energy_col]].copy()
process_df[annual_energy_col] = pd.to_numeric(process_df[annual_energy_col], errors="coerce")
process_df = (
    process_df.dropna(subset=[industrial_process_col, annual_energy_col])
    .groupby(industrial_process_col, as_index=False)[annual_energy_col]
    .sum()
    .rename(columns={industrial_process_col: "Industrial process", annual_energy_col: "Annual Energy"})
)
process_df = process_df[process_df["Annual Energy"] > 0].copy()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Annual Energy Breakdown for {selected_naics}")

if not breakdown_df.empty:
    fig_donut = px.pie(
        breakdown_df,
        names="Type",
        values="Value",
        hole=0.55,
        color="Type",
        color_discrete_map={
            "Annual Fuels": "#f7901d",
            "Annual Steam": "#3b82f6",
            "Annual Electricity": "#0f766e",
        },
    )
    fig_donut.update_traces(textinfo="percent+label", textposition="outside")
    fig_donut.update_layout(showlegend=False, margin=dict(t=20, b=10, l=10, r=10))
    st.plotly_chart(fig_donut, use_container_width=True)
else:
    st.info("No annual energy breakdown is available for this selection.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Annual Energy for NAICS (6-digit) code sectors within {selected_naics}")

if not bar_df.empty:
    bar_display = bar_df.sort_values("Annual Energy", ascending=False).copy()
    bar_display["Annual Energy"] = bar_display["Annual Energy"].map(lambda x: f"{x:,.2f} PJ")
    st.dataframe(bar_display, use_container_width=True, hide_index=True)
else:
    st.info("No NAICS Level 2 annual energy data is available for this selection.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(f"Annual Energy for Industrial Processes within {selected_naics}")

if not process_df.empty:
    process_display = process_df.sort_values("Annual Energy", ascending=False).copy()
    process_display["Annual Energy"] = process_display["Annual Energy"].map(lambda x: f"{x:,.2f} PJ")
    st.dataframe(process_display, use_container_width=True, hide_index=True)
else:
    st.info("No industrial process annual energy data is available for this selection.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
