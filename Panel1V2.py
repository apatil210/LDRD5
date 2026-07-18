from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.io as pio
import requests
import streamlit as st

st.set_page_config(
    page_title="US Manufacturing Energy Classification",
    layout="wide"
)

pio.templates.default = "plotly"

DATA_URL = "https://raw.githubusercontent.com/apatil210/LDRD4/main/WebsiteEngine3.xlsx"

TEXT_COLOR = "#14212B"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
BAR_COLOR = "#0B6E74"

SEC_COLOR_MAP = {
    "SEC Electricity": "#54A24B",
    "SEC Fuels": "#F58518",
    "SEC Steam": "#4C78A8",
}

TEMP_COLOR_MAP = {
    "<20 °C": "#54A24B",
    "20-100 °C": "#B5CF6B",
    "100-200 °C": "#EECA3B",
    "200-400 °C": "#F58518",
    "400-600 °C": "#E45756",
    ">=600 °C": "#B279A2",
}


@st.cache_data(show_spinner=False)
def load_excel(url: str) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type.lower():
        raise ValueError("URL returned an HTML page instead of an Excel file.")

    raw_df = pd.read_excel(
        BytesIO(response.content),
        sheet_name="Process-level data",
        header=None,
        engine="openpyxl"
    )

    header_row_idx = 1
    df = raw_df.iloc[header_row_idx + 2:].copy()
    df.columns = raw_df.iloc[header_row_idx].astype(str).str.strip()
    df = df.reset_index(drop=True)

    return df


def clean_category(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )


def prepare_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    category_col = "Industrial process"
    value_col = "Percent Annual energy demand in 2022"

    df_work = df[[category_col, value_col]].copy()
    df_work[category_col] = clean_category(df_work[category_col])
    df_work[value_col] = pd.to_numeric(df_work[value_col], errors="coerce").fillna(0)

    df_agg = (
        df_work.groupby(category_col, as_index=False)[value_col]
        .sum()
        .sort_values(value_col, ascending=False)
        .reset_index(drop=True)
    )

    df_agg = df_agg[df_agg[value_col] > 0].copy()
    df_agg["Display Percent"] = df_agg[value_col] * 100
    df_agg["Rank"] = range(1, len(df_agg) + 1)

    return df_agg


def build_bar_chart(df: pd.DataFrame):
    break_start = 8.0
    break_end = 21.0
    compressed_gap = 1.2

    def transform_value(x):
        if x <= break_start:
            return x
        return break_start + compressed_gap + (x - break_end)

    chart_df = df.copy()
    chart_df["Plot Value"] = chart_df["Display Percent"].apply(transform_value)

    fig = px.bar(
        chart_df,
        x="Plot Value",
        y="Industrial process",
        orientation="h",
        text="Display Percent",
        color_discrete_sequence=[BAR_COLOR]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Percent annual energy: %{text:.2f}%<extra></extra>"
        ),
        marker=dict(line=dict(color="#FCFCFA", width=1.2))
    )

    max_display = chart_df["Display Percent"].max()
    max_plot = transform_value(max_display) + 0.8

    fig.update_layout(
        width=1500,
        height=max(700, 32 * len(chart_df)),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        margin=dict(t=60, l=280, r=120, b=20),
        xaxis_title="Contribution of Industrial Processes to Total Energy Demand (%)",
        yaxis_title="",
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=14
        ),
        shapes=[
            dict(
                type="line",
                x0=break_start + 0.35,
                x1=break_start + 0.55,
                y0=-0.5,
                y1=len(chart_df) - 0.5,
                xref="x",
                yref="y",
                line=dict(color="white", width=6)
            ),
            dict(
                type="line",
                x0=break_start + 0.65,
                x1=break_start + 0.85,
                y0=-0.5,
                y1=len(chart_df) - 0.5,
                xref="x",
                yref="y",
                line=dict(color="white", width=6)
            )
        ]
    )

    fig.update_xaxes(
        range=[0, max_plot + 0.8],
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4, 5, 6, 7, break_start + compressed_gap],
        ticktext=["0%", "1%", "2%", "3%", "4%", "5%", "6%", "7%", "21%"],
        showgrid=True,
        automargin=True
    )

    fig.update_yaxes(
        categoryorder="total ascending",
        automargin=True
    )

    return fig


def build_sec_donut(fact_sheet: dict):
    donut_df = pd.DataFrame({
        "SEC Type": ["Electricity", "Fuels", "Steam"],
        "Value": [
            fact_sheet["SEC Electricity"],
            fact_sheet["SEC Fuels"],
            fact_sheet["SEC Steam"]
        ]
    })

    donut_df = donut_df[donut_df["Value"] > 0].copy()

    fig = px.pie(
        donut_df,
        names="SEC Type",
        values="Value",
        hole=0.62,
        color="SEC Type",
        color_discrete_map=SEC_COLOR_MAP
    )

    total_sec = donut_df["Value"].sum()

    fig.update_traces(
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{value:.3f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
        marker=dict(line=dict(color="#FFFFFF", width=2))
    )

    fig.update_layout(
        height=360,
        margin=dict(t=20, l=20, r=20, b=20),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        showlegend=False,
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=13
        ),
        annotations=[
            dict(
                text=f"<b>Total SEC (GJ/t)</b><br>{total_sec:.2f}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )
        ]
    )

    return fig


def build_temp_sec_donut(fact_sheet: dict):
    donut_df = fact_sheet["Temperature SEC Breakdown"].copy()
    donut_df = donut_df[donut_df["Value"] > 0].copy()

    fig = px.pie(
        donut_df,
        names="Temperature Range",
        values="Value",
        hole=0.62,
        color="Temperature Range",
        color_discrete_map=TEMP_COLOR_MAP
    )

    total_sec = donut_df["Value"].sum()

    fig.update_traces(
        textposition="outside",
        texttemplate="%{label}<br>%{percent}",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{value:.3f} GJ/t<br>"
            "Share: %{percent}<extra></extra>"
        ),
        marker=dict(line=dict(color="#FFFFFF", width=2))
    )

    fig.update_layout(
        height=360,
        margin=dict(t=20, l=20, r=20, b=20),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        showlegend=False,
        font=dict(
            family="Arial, sans-serif",
            color=TEXT_COLOR,
            size=13
        ),
        annotations=[
            dict(
                text=f"<b>Total SEC (GJ/t)</b><br>{total_sec:.2f}",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )
        ]
    )

    return fig


def build_fact_sheet(df: pd.DataFrame, selected_process: str):
    process_col = "Industrial process"
    unit_ops_col = "Unit operation (Level 3 classification; with details)"
    production_col = "Annual production in 2022\n(based on FU)"
    annual_energy_col = "Annual energy demand in 2022"

    sec_total_col = "SEC"

    # Excel columns U, W, X, Y -> zero-based positions 20, 22, 23, 24
    temp_sec_idx = 20
    elec_idx = 22
    fuel_idx = 23
    steam_idx = 24

    temp_web_col = "Process Temperature for Webpage"
    process_temp_col = "Process temperature"
    inlet_temp_col = "Inlet temperature"
    outlet_temp_col = "Outlet temperature"
    process_pressure_col = "Process pressure"
    inlet_pressure_col = "Inlet pressure"
    outlet_pressure_col = "Outlet pressure"
    residence_time_col = "Residence time"
    efficiency_col = "Efficiency"

    naics_idx = 45

    fact_df = df.copy()
    fact_df[process_col] = clean_category(fact_df[process_col])
    fact_df[unit_ops_col] = clean_category(fact_df[unit_ops_col])

    selected_df = fact_df[fact_df[process_col] == selected_process].copy()

    if selected_df.empty:
        return None

    numeric_cols = [
        production_col,
        annual_energy_col,
        sec_total_col,
        temp_web_col,
        process_temp_col
    ]

    for col in numeric_cols:
        if col in selected_df.columns:
            selected_df[col] = pd.to_numeric(selected_df[col], errors="coerce")

    selected_df.iloc[:, temp_sec_idx] = pd.to_numeric(selected_df.iloc[:, temp_sec_idx], errors="coerce")
    selected_df.iloc[:, elec_idx] = pd.to_numeric(selected_df.iloc[:, elec_idx], errors="coerce")
    selected_df.iloc[:, fuel_idx] = pd.to_numeric(selected_df.iloc[:, fuel_idx], errors="coerce")
    selected_df.iloc[:, steam_idx] = pd.to_numeric(selected_df.iloc[:, steam_idx], errors="coerce")

    selected_df["Temp for Donut"] = selected_df[temp_web_col]
    if process_temp_col in selected_df.columns:
        selected_df["Temp for Donut"] = selected_df["Temp for Donut"].fillna(selected_df[process_temp_col])

    # Use Column U directly for temperature donut SEC values
    selected_df["Temp SEC Value"] = selected_df.iloc[:, temp_sec_idx]

    naics_series = (
        selected_df.iloc[:, naics_idx]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda s: s.ne("") & s.ne("nan") & s.ne("None")]
        .unique()
    )
    naics_code = naics_series[0] if len(naics_series) > 0 else "N/A"

    production_values = (
        selected_df[production_col]
        .dropna()
        .loc[lambda s: s != 0]
        .unique()
    )
    annual_production = production_values[0] if len(production_values) > 0 else 0
    annual_energy = selected_df[annual_energy_col].fillna(0).sum()

    sec_electricity = selected_df.iloc[:, elec_idx].fillna(0).sum()
    sec_fuels = selected_df.iloc[:, fuel_idx].fillna(0).sum()
    sec_steam = selected_df.iloc[:, steam_idx].fillna(0).sum()

    temp_sec_df = selected_df[["Temp for Donut", "Temp SEC Value"]].copy()
    temp_sec_df = temp_sec_df.dropna(subset=["Temp for Donut"]).copy()
    temp_sec_df = temp_sec_df[temp_sec_df["Temp SEC Value"].fillna(0) > 0].copy()

    temp_sec_df["Temperature Range"] = pd.cut(
        temp_sec_df["Temp for Donut"],
        bins=[float("-inf"), 20, 100, 200, 400, 600, float("inf")],
        labels=[
        "<20 °C",
        "20-100 °C",
        "100-200 °C",
        "200-400 °C",
        "400-600 °C",
        ">=600 °C"
    ],
    right=False
    )

    temp_breakdown = (
        temp_sec_df.groupby("Temperature Range", observed=False, as_index=False)["Temp SEC Value"]
        .sum()
        .rename(columns={"Temp SEC Value": "Value"})
    )

    all_ranges = pd.DataFrame({
       "Temperature Range": [
        "<20 °C",
        "20-100 °C",
        "100-200 °C",
        "200-400 °C",
        "400-600 °C",
        ">=600 °C"
    ]
    })

    temp_breakdown = all_ranges.merge(
        temp_breakdown,
        on="Temperature Range",
        how="left"
    )
    temp_breakdown["Value"] = temp_breakdown["Value"].fillna(0)

    detail_df = pd.DataFrame({
        "Unit Operations": selected_df[unit_ops_col],
        # "SEC Total (GJ/t)": selected_df[sec_total_col],
        "SEC Total (GJ/t)": selected_df.iloc[:, temp_sec_idx],
        "SEC Electricity (GJ/t)": selected_df.iloc[:, elec_idx],
        "SEC Fuels (GJ/t)": selected_df.iloc[:, fuel_idx],
        "SEC Fuels or Electricity for Steam or Steam from CHP (GJ/t)": selected_df.iloc[:, steam_idx],
        # "Process Temp for Webpage (°C)": selected_df[temp_web_col],
        "Process temperature (°C)": selected_df[temp_web_col],
        # "Inlet temperature (°C)": selected_df[inlet_temp_col],
        # "Outlet temperature (°C)": selected_df[outlet_temp_col],
        # "Efficiency (%)": selected_df[efficiency_col],
        "Process pressure (bar)": selected_df[process_pressure_col],
        # "Inlet pressure (bar)": selected_df[inlet_pressure_col],
        # "Outlet pressure (bar)": selected_df[outlet_pressure_col],
        # "Residence time (sec)": selected_df[residence_time_col]
    })

    return {
        "Annual Production": annual_production,
        "Annual Energy": annual_energy,
        "NAICS Code": naics_code,
        "SEC Electricity": sec_electricity,
        "SEC Fuels": sec_fuels,
        "SEC Steam": sec_steam,
        "Rows": selected_df.shape[0],
        "Details": detail_df,
        "Temperature SEC Breakdown": temp_breakdown
    }


st.title("2022 U.S. Manufacturing Energy Consumption by Industrial Process")

try:
    df = load_excel(DATA_URL)
    bar_df = prepare_bar_data(df)

    left_col, right_col = st.columns([1.6, 1.1], gap="large")

    with left_col:
        st.subheader("Annual Energy Consumption by Industrial Process (%)")

        st.plotly_chart(
                build_bar_chart(bar_df),
                use_container_width=False,
                theme=None,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False
                }
            )

    with right_col:
        selected_process = st.selectbox(
    "Select an industrial process to view its energy demand breakdown. "
    "Note that the production units for some processes differ from million tonnes of product and are defined as follows: "
    "barrels of crude for Petroleum Refining (324110), bushels of corn for Wet Corn Milling (311221), "
    "million tonnes of raw milk input for Fluid Milk Manufacturing (3115), million tonnes of soybeans input for Soybean Processing (311224), "
    "barrels of beer for Beer Processing (312120), million tonnes of scrap input for Secondary Aluminum (331313), "
    "cubic meters of spirits for Distillery (312140) and vehicle units for Automotive Assembly (336110)",
    bar_df["Industrial process"].tolist()
)

        fact_sheet = build_fact_sheet(df, selected_process)

        if fact_sheet:
            c1, c2, c3 = st.columns(3)
            c1.metric("Annual Production (million-tonne/yr)", f"{fact_sheet['Annual Production']:.2f}")
            c2.metric("Annual Energy (PJ/yr)", f"{fact_sheet['Annual Energy']:.2f}")
            c3.metric("NAICS Code", f"{fact_sheet['NAICS Code']}")

            st.subheader("Specific Energy Consumption (SEC)")

            st.caption("Categorization by Energy Source")
            st.plotly_chart(
                build_sec_donut(fact_sheet),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False}
            )

            st.caption("Categorization by Process Temperature")
            st.plotly_chart(
                build_temp_sec_donut(fact_sheet),
                use_container_width=True,
                theme=None,
                config={"displayModeBar": False}
            )

            st.dataframe(
                fact_sheet["Details"],
                use_container_width=True,
                hide_index=True
            )

except Exception as e:
    st.error(f"App error: {e}")
