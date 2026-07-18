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
DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD5/main/WebsiteEngine3.xlsx"

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
    "Fuels": "#C05A00",
    "Steam": "#355C9A",
    "Electricity": "#1F8A4C",
}

TEMP_COLORS_SI = {
    "<20 °C": "#2A9D8F",
    "20-100 °C": "#7FBF7B",
    "100-200 °C": "#B9770E",
    "200-400 °C": "#C0392B",
    "400-600 °C": "#8E5EA2",
    ">=600 °C": "#5B2C6F",
}

TEMP_COLORS_IMPERIAL = {
    "<68 °F": "#2A9D8F",
    "68-212 °F": "#7FBF7B",
    "212-392 °F": "#B9770E",
    "392-752 °F": "#C0392B",
    "752-1112 °F": "#8E5EA2",
    ">=1112 °F": "#5B2C6F",
}

TEMP_LABEL_MAP_SI_TO_IMPERIAL = {
    "<20 °C": "<68 °F",
    "20-100 °C": "68-212 °F",
    "100-200 °C": "212-392 °F",
    "200-400 °C": "392-752 °F",
    "400-600 °C": "752-1112 °F",
    ">=600 °C": ">=1112 °F",
}

TEMP_ORDER_SI = [
    "<20 °C",
    "20-100 °C",
    "100-200 °C",
    "200-400 °C",
    "400-600 °C",
    ">=600 °C",
]

TEMP_ORDER_IMPERIAL = [
    "<68 °F",
    "68-212 °F",
    "212-392 °F",
    "392-752 °F",
    "752-1112 °F",
    ">=1112 °F",
]


def norm(x):
    return " ".join(
        str(x).replace("\n", " ").replace("(", "").replace(")", "").strip().split()
    ).lower()


def pick_col(df, target):
    matches = [c for c in df.columns if norm(c) == norm(target)]
    return matches[0] if matches else None


def num(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def pj_to_tbtu(x):
    return x * 0.947817


def c_to_f(x):
    return x * 9 / 5 + 32


def fmt_energy(x, unit_system):
    return f"{x:,.2f} {'PJ' if unit_system == 'SI' else 'TBtu'}"


def fmt_percent(x):
    return f"{x:.2%}" if x > 0 else "N/A"


def style_donut(fig, energy_unit):
    fig.update_traces(
        domain=dict(x=[0.00, 0.72]),
        textinfo="percent",
        hovertemplate=f"%{{label}}<br>%{{value:,.2f}} {energy_unit}<br>%{{percent}}<extra></extra>",
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


def convert_temp_labels(temp_grouped_df, unit_system):
    temp_grouped_df = temp_grouped_df.copy()

    if unit_system == "Imperial":
        temp_grouped_df["Temperature Range"] = temp_grouped_df["Temperature Range"].astype(str).map(
            lambda x: TEMP_LABEL_MAP_SI_TO_IMPERIAL.get(x, x)
        )
    else:
        temp_grouped_df["Temperature Range"] = temp_grouped_df["Temperature Range"].astype(str)

    return temp_grouped_df


def render_overview(
    data_subset,
    subtitle,
    unit_system,
    show_naics_chart=True,
    show_process_chart=True,
    show_energy_chart=True,
    show_temp_chart=True,
    coverage_col=None,
    coverage_label="Database coverage",
):
    total_energy = num(data_subset[total_energy_col]).sum()
    total_electricity = num(data_subset[electricity_col]).sum()
    total_fuels = num(data_subset[fuels_col]).sum()
    total_steam = num(data_subset[steam_col]).sum()

    if unit_system == "Imperial":
        total_energy = pj_to_tbtu(total_energy)
        total_electricity = pj_to_tbtu(total_electricity)
        total_fuels = pj_to_tbtu(total_fuels)
        total_steam = pj_to_tbtu(total_steam)

    energy_unit = "PJ" if unit_system == "SI" else "TBtu"

    coverage_source_col = coverage_col if coverage_col is not None else percent_coverage_col
    coverage_value = num(data_subset[coverage_source_col]).sum()
    coverage_text = fmt_percent(coverage_value)

    st.subheader(subtitle)

    st.markdown(f"""
    <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:1.5rem;">
        <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Total annual energy<br><b>{fmt_energy(total_energy, unit_system)}</b></div>
        <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual electricity<br><b>{fmt_energy(total_electricity, unit_system)}</b></div>
        <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual fuels<br><b>{fmt_energy(total_fuels, unit_system)}</b></div>
        <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">Annual steam<br><b>{fmt_energy(total_steam, unit_system)}</b></div>
        <div style="padding:1rem; border:1px solid #ddd; border-radius:12px;">{coverage_label}<br><b>{coverage_text}</b></div>
    </div>
    """, unsafe_allow_html=True)

    breakdown_df = pd.DataFrame({
        "Type": ["Fuels", "Steam", "Electricity"],
        "Value": [total_fuels, total_steam, total_electricity],
    })
    breakdown_df = breakdown_df[breakdown_df["Value"] > 0].copy()

    naics_donut_df = (
        data_subset[[naics_l2_col, total_energy_col]]
        .assign(**{total_energy_col: pd.to_numeric(data_subset[total_energy_col], errors="coerce")})
        .dropna(subset=[naics_l2_col, total_energy_col])
        .groupby(naics_l2_col, as_index=False)[total_energy_col]
        .sum()
        .rename(columns={naics_l2_col: "NAICS Level 2", total_energy_col: "Annual Energy"})
    )
    naics_donut_df = naics_donut_df[
        naics_donut_df["Annual Energy"] > 0
    ].sort_values("Annual Energy", ascending=False)

    process_df = (
        data_subset[[industrial_process_col, total_energy_col]]
        .assign(**{total_energy_col: pd.to_numeric(data_subset[total_energy_col], errors="coerce")})
        .dropna(subset=[industrial_process_col, total_energy_col])
        .groupby(industrial_process_col, as_index=False)[total_energy_col]
        .sum()
        .rename(columns={industrial_process_col: "Industrial process", total_energy_col: "Annual Energy"})
    )
    process_df = process_df[
        process_df["Annual Energy"] > 0
    ].sort_values("Annual Energy", ascending=False)

    temp_df = data_subset[[temperature_col, total_energy_col]].copy()
    temp_df.columns = ["Temperature", "Annual Energy"]
    temp_df["Temperature"] = pd.to_numeric(temp_df["Temperature"], errors="coerce")
    temp_df["Annual Energy"] = pd.to_numeric(temp_df["Annual Energy"], errors="coerce")
    temp_df = temp_df.dropna(subset=["Temperature"])
    temp_df = temp_df[temp_df["Annual Energy"] > 0].copy()

    if unit_system == "Imperial":
        temp_df["Annual Energy"] = temp_df["Annual Energy"].apply(pj_to_tbtu)

    temp_df["Temperature Range"] = pd.cut(
        temp_df["Temperature"],
        bins=[-float("inf"), 20, 100, 200, 400, 600, float("inf")],
        labels=TEMP_ORDER_SI,
        right=False,
    )

    temp_donut_df = (
        temp_df.dropna(subset=["Temperature Range"])
        .groupby("Temperature Range", as_index=False, observed=False)["Annual Energy"]
        .sum()
    )
    temp_donut_df = temp_donut_df[temp_donut_df["Annual Energy"] > 0].copy()
    temp_donut_df = convert_temp_labels(temp_donut_df, unit_system)

    temp_color_map = TEMP_COLORS_SI if unit_system == "SI" else TEMP_COLORS_IMPERIAL
    temp_order = TEMP_ORDER_SI if unit_system == "SI" else TEMP_ORDER_IMPERIAL

    if unit_system == "Imperial":
        naics_donut_df["Annual Energy"] = naics_donut_df["Annual Energy"].apply(pj_to_tbtu)
        process_df["Annual Energy"] = process_df["Annual Energy"].apply(pj_to_tbtu)

    if show_naics_chart or show_process_chart:
        col1, col2 = st.columns(2)

        with col1:
            if show_naics_chart and not naics_donut_df.empty:
                fig = px.pie(
                    naics_donut_df,
                    names="NAICS Level 2",
                    values="Annual Energy",
                    hole=0.62,
                    color="NAICS Level 2",
                    color_discrete_sequence=NAICS_COLORS,
                    title="NAICS Subsectors Within",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)

            if show_process_chart and not process_df.empty:
                fig = px.pie(
                    process_df,
                    names="Industrial process",
                    values="Annual Energy",
                    hole=0.62,
                    color="Industrial process",
                    color_discrete_sequence=PROCESS_COLORS,
                    title="Industrial Processes Within",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if show_energy_chart and not breakdown_df.empty:
                fig = px.pie(
                    breakdown_df,
                    names="Type",
                    values="Value",
                    hole=0.62,
                    color="Type",
                    color_discrete_map=ENERGY_SOURCE_COLORS,
                    title="Distribution by Energy Source",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)

            if show_temp_chart and not temp_donut_df.empty:
                fig = px.pie(
                    temp_donut_df,
                    names="Temperature Range",
                    values="Annual Energy",
                    hole=0.62,
                    color="Temperature Range",
                    color_discrete_map=temp_color_map,
                    category_orders={"Temperature Range": temp_order},
                    title="Distribution by Process Temperature",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)

    else:
        col1, col2 = st.columns(2)

        with col1:
            if show_energy_chart and not breakdown_df.empty:
                fig = px.pie(
                    breakdown_df,
                    names="Type",
                    values="Value",
                    hole=0.62,
                    color="Type",
                    color_discrete_map=ENERGY_SOURCE_COLORS,
                    title="Distribution by Energy Source",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if show_temp_chart and not temp_donut_df.empty:
                fig = px.pie(
                    temp_donut_df,
                    names="Temperature Range",
                    values="Annual Energy",
                    hole=0.62,
                    color="Temperature Range",
                    color_discrete_map=temp_color_map,
                    category_orders={"Temperature Range": temp_order},
                    title="Distribution by Process Temperature",
                )
                fig = style_donut(fig, energy_unit)
                st.plotly_chart(fig, use_container_width=True)


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
percent_coverage_col = pick_col(df, "Percent Coverage of NAICS (3-digit) Sector")

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

unit_system = st.radio(
    "Select unit system",
    ["SI", "Imperial"],
    horizontal=True,
    key="unit_system"
)

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

tab1, tab2 = st.tabs(["Selected NAICS", "Consolidated Overview"])

with tab1:
    render_overview(
        df_filtered,
        f"Selected category: {selected_naics}",
        unit_system=unit_system,
        show_naics_chart=True,
        show_process_chart=True,
        show_energy_chart=True,
        show_temp_chart=True,
        coverage_col=percent_coverage_col,
        coverage_label="Database coverage",
    )

with tab2:
    render_overview(
        df,
        "All NAICS Categories Combined",
        unit_system=unit_system,
        show_naics_chart=False,
        show_process_chart=False,
        show_energy_chart=True,
        show_temp_chart=True,
        coverage_col=percent_energy_col,
        coverage_label="Database Coverage",
    )
