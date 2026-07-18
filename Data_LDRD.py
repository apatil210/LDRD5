import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import colorsys
import requests
from io import BytesIO
from matplotlib.colors import to_rgb, to_hex
from plotly.subplots import make_subplots

st.set_page_config(page_title="US Manufacturing Energy 2022", layout="wide")
st.title("US Manufacturing Energy 2022")


@st.cache_data
def load_excel(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


def make_shades(base_color, n, light_factor=0.25):
    rgb = np.array(to_rgb(base_color))
    light_rgb = 1 - (1 - rgb) * light_factor
    return [
        to_hex(light_rgb + (rgb - light_rgb) * t)
        for t in np.linspace(1, 0, n)
    ]


def generate_distinct_colors(n, s=0.65, v=0.80):
    colors = []
    golden_ratio = 0.61803398875
    h = 0.11
    for _ in range(n):
        h = (h + golden_ratio) % 1
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        colors.append("#{0:02X}{1:02X}{2:02X}".format(
            int(r * 255), int(g * 255), int(b * 255)
        ))
    return colors


def build_figure1():
    file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure1Data.xlsx"
    base_color = "#474646"
    light_factor = 0.001

    df = load_excel(file_url)

    required_columns = {"Category", "Data"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Figure 1 is missing required columns: {required_columns}")

    df_agg = df.groupby("Category", as_index=False)["Data"].sum()
    df_agg = df_agg[df_agg["Data"] > 0].copy()
    df_agg = df_agg.sort_values("Data", ascending=False).reset_index(drop=True)

    if df_agg.empty:
        raise ValueError("Figure 1 has no positive data values.")

    categories = df_agg["Category"]
    values = df_agg["Data"]
    colors = make_shades(base_color, len(values), light_factor)

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.15, 0.85],
        vertical_spacing=0.03
    )

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker=dict(color=colors, line=dict(color="black", width=1)),
            hovertemplate="%{x}<br>%{y:.1%}<extra></extra>"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker=dict(color=colors, line=dict(color="black", width=1)),
            hovertemplate="%{x}<br>%{y:.1%}<extra></extra>"
        ),
        row=2, col=1
    )

    fig.update_yaxes(range=[0.19, 0.20], tickformat=".0%", row=1, col=1)
    fig.update_yaxes(range=[0.00, 0.07], tickformat=".0%", row=2, col=1)
    fig.update_xaxes(showticklabels=False, row=1, col=1)
    fig.update_xaxes(showticklabels=True, tickangle=45, row=2, col=1)

    fig.update_layout(
        height=700,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=40, b=40, l=60, r=30)
    )
    return fig


def build_figure2():
    file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure2Data.xlsx"
    df = load_excel(file_url)

    required_columns = {"Category", "Data"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Figure 2 is missing required columns: {required_columns}")

    df_agg = df.groupby("Category", as_index=False)["Data"].sum()
    df_agg = df_agg[df_agg["Data"] > 0].copy()
    df_agg = df_agg.sort_values("Data", ascending=False).reset_index(drop=True)

    if df_agg.empty:
        raise ValueError("Figure 2 has no positive data values.")

    total = df_agg["Data"].sum()
    df_agg["Share_pct"] = 100 * df_agg["Data"] / total
    df_agg["Category_clean"] = df_agg["Category"].astype(str).str.replace("_", " ", regex=False)

    df_agg["Display_text"] = df_agg.apply(
        lambda r: f"<b>{r['Category_clean']}</b><br>{r['Share_pct']:.1f}%"
        if r["Share_pct"] >= 1 else "",
        axis=1
    )

    categories = df_agg["Category_clean"].unique()
    palette = generate_distinct_colors(len(categories))
    color_map = dict(zip(categories, palette))

    fig = px.treemap(
        df_agg,
        path=["Category_clean"],
        values="Data",
        color="Category_clean",
        color_discrete_map=color_map,
        custom_data=["Share_pct", "Data", "Display_text"]
    )

    fig.update_traces(
        texttemplate="%{customdata[2]}",
        textfont_size=20,
        marker=dict(line=dict(color="white", width=2), cornerradius=5),
        tiling=dict(pad=3),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: %{customdata[1]:.3f}<br>"
            "Share: %{customdata[0]:.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        # title=dict(text="Unit Operation Level 2", x=0.5),
        paper_bgcolor="white",
        margin=dict(t=70, l=10, r=10, b=10),
        height=700
    )
    return fig


def build_figure3():
    file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure3Data.xlsx"
    value_cols = ["Electricity", "Fuel", "Steam"]

    df = load_excel(file_url)

    required_columns = {"Category", "Electricity", "Fuel", "Steam"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Figure 3 is missing required columns: {required_columns}")

    df_agg = df.groupby("Category", as_index=False)[value_cols].sum()
    df_agg["Category_clean"] = df_agg["Category"].astype(str).str.replace("_", " ", regex=False)
    df_agg = df_agg[(df_agg[value_cols] > 0).any(axis=1)].copy()

    if df_agg.empty:
        raise ValueError("Figure 3 has no positive values.")

    base_palette = [
        "#A000FF", "#00D000", "#E00060", "#C6E000", "#C07030",
        "#3C7CFF", "#00B0FF", "#00C0A0", "#FF8000", "#FF00AA"
    ]

    categories = df_agg["Category_clean"].tolist()
    n_cat = len(categories)
    palette = (base_palette * ((n_cat // len(base_palette)) + 1))[:n_cat]
    color_map = dict(zip(categories, palette))

    def make_labels(df_in, value_col):
        total = df_in[value_col].sum()
        out = df_in.copy()
        out = out[out[value_col] > 0].copy()
        out["Share_pct"] = 100 * out[value_col] / total if total > 0 else 0
        out["Display_text"] = out.apply(
            lambda r: f"<b>{r['Category_clean']}</b><br>{r['Share_pct']:.1f}%"
            if r["Share_pct"] >= 1 else "",
            axis=1
        )
        return out

    elec_df = make_labels(df_agg, "Electricity")
    fuel_df = make_labels(df_agg, "Fuel")
    steam_df = make_labels(df_agg, "Steam")

    fig = make_subplots(
        rows=1,
        cols=3,
        specs=[[{"type": "domain"}, {"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Electricity", "Fuel", "Steam")
    )

    common_textfont = dict(size=18, color="white")

    fig.add_trace(
        go.Treemap(
            labels=elec_df["Category_clean"],
            parents=[""] * len(elec_df),
            values=elec_df["Electricity"],
            customdata=elec_df[["Share_pct", "Electricity", "Display_text"]].values,
            texttemplate="%{customdata[2]}",
            textfont=common_textfont,
            marker=dict(
                colors=[color_map[c] for c in elec_df["Category_clean"]],
                line=dict(color="white", width=2)
            ),
            tiling=dict(pad=3),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Value: %{customdata[1]:.3f}<br>"
                "Share: %{customdata[0]:.2f}%"
                "<extra></extra>"
            ),
            branchvalues="total",
            name="Electricity"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Treemap(
            labels=fuel_df["Category_clean"],
            parents=[""] * len(fuel_df),
            values=fuel_df["Fuel"],
            customdata=fuel_df[["Share_pct", "Fuel", "Display_text"]].values,
            texttemplate="%{customdata[2]}",
            textfont=common_textfont,
            marker=dict(
                colors=[color_map[c] for c in fuel_df["Category_clean"]],
                line=dict(color="white", width=2)
            ),
            tiling=dict(pad=3),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Value: %{customdata[1]:.3f}<br>"
                "Share: %{customdata[0]:.2f}%"
                "<extra></extra>"
            ),
            branchvalues="total",
            name="Fuel"
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Treemap(
            labels=steam_df["Category_clean"],
            parents=[""] * len(steam_df),
            values=steam_df["Steam"],
            customdata=steam_df[["Share_pct", "Steam", "Display_text"]].values,
            texttemplate="%{customdata[2]}",
            textfont=common_textfont,
            marker=dict(
                colors=[color_map[c] for c in steam_df["Category_clean"]],
                line=dict(color="white", width=2)
            ),
            tiling=dict(pad=3),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Value: %{customdata[1]:.3f}<br>"
                "Share: %{customdata[0]:.2f}%"
                "<extra></extra>"
            ),
            branchvalues="total",
            name="Steam"
        ),
        row=1, col=3
    )

    fig.update_layout(
       # title=dict(text="Energy Classification by Utility Source", x=0.5),
        paper_bgcolor="white",
        margin=dict(t=80, l=10, r=10, b=10),
        height=700
    )
    return fig


def build_figure4():
    df = pd.DataFrame({
        "Category": [
            "Food (311)",
            "Beverage and Tobacco Products (312)",
            "Wood Products (321)",
            "Paper (322)",
            "Petroleum and Coal Products (324)",
            "Chemicals (325)",
            "Nonmetallic Mineral Products (327)",
            "Primary Metals (331)",
            "Fabricated Metal Products (332)",
            "Transportation Equipment (336)"
        ],
        "LDRD Coverage": [532, 58, 165, 1593, 3239, 1824, 465, 1228, 69, 75],
        "Uncovered": [703, 207, 249, 410, 304, 2152, 701, 221, 356, 229],
        "Pct LDRD Coverage": [43, 22, 40, 80, 91, 46, 40, 85, 16, 25],
        "Total MECS 2022": [1235, 265, 414, 2003, 3543, 3976, 1166, 1449, 425, 304]
    })

    covered_text = [
        f"{v}%"
        if cov >= 120 else ""
        for v, cov in zip(df["Pct LDRD Coverage"], df["LDRD Coverage"])
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Category"],
            y=df["LDRD Coverage"],
            name="LDRD Coverage",
            marker_color="#2E86AB",
            text=covered_text,
            textposition="inside",
            textfont=dict(color="white", size=12),
            customdata=np.stack(
                [df["Pct LDRD Coverage"], df["Total MECS 2022"]],
                axis=-1
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "LDRD Coverage: %{y:,}<br>"
                "% LDRD Coverage: %{customdata[0]}%<br>"
                "Total MECS 2022: %{customdata[1]:,}"
                "<extra></extra>"
            )
        )
    )

    fig.add_trace(
        go.Bar(
            x=df["Category"],
            y=df["Uncovered"],
            name="Uncovered",
            marker_color="#CFCFCF",
            customdata=np.stack(
                [df["Pct LDRD Coverage"], df["Total MECS 2022"]],
                axis=-1
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Uncovered: %{y:,}<br>"
                "% LDRD Coverage: %{customdata[0]}%<br>"
                "Total MECS 2022: %{customdata[1]:,}"
                "<extra></extra>"
            )
        )
    )

    for i, total in enumerate(df["Total MECS 2022"]):
        fig.add_annotation(
            x=df["Category"][i],
            y=total,
            text=f"{total:,}",
            showarrow=False,
            yshift=14,
            font=dict(size=11, color="black")
        )

    fig.update_layout(
       # title=dict(text="Total MECS 2022 with % LDRD Coverage", x=0.5),
        barmode="stack",
        xaxis=dict(title="", tickangle=45),
        yaxis=dict(title="Total MECS 2022", gridcolor="rgba(0,0,0,0.1)"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", y=1.08, x=0),
        margin=dict(t=90, b=120, l=60, r=30),
        height=700
    )

    return fig


try:
    fig1 = build_figure1()
    fig2 = build_figure2()
    fig3 = build_figure3()
    fig4 = build_figure4()
except Exception as e:
    st.error(f"App error: {e}")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "Energy Summary 50+ US Industries",
    "Energy Classification: Unit Operations",
    "Energy Classification: Utility Source",
    "Energy Classification: NAICS"
])

with tab1:
    st.plotly_chart(fig1, use_container_width=True, key="fig1")

with tab2:
    st.plotly_chart(fig2, use_container_width=True, key="fig2")

with tab3:
    st.plotly_chart(fig3, use_container_width=True, key="fig3")

with tab4:
    st.plotly_chart(fig4, use_container_width=True, key="fig4")
