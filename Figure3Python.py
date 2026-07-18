import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Figure 3", layout="wide")

file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure3Data.xlsx"
value_cols = ["Electricity", "Fuel", "Steam"]


@st.cache_data
def load_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


def make_labels(df_in, value_col):
    total = df_in[value_col].sum()
    out = df_in.copy()
    out = out[out[value_col] > 0].copy()

    if total > 0:
        out["Share_pct"] = 100 * out[value_col] / total
    else:
        out["Share_pct"] = 0

    out["Display_text"] = out.apply(
        lambda r: f"<b>{r['Category_clean']}</b><br>{r['Share_pct']:.1f}%"
        if r["Share_pct"] >= 1 else "",
        axis=1
    )
    return out


try:
    df = load_data(file_url)
except Exception as e:
    st.error(f"Failed to load Excel file: {e}")
    st.stop()

required_columns = {"Category", "Electricity", "Fuel", "Steam"}
if not required_columns.issubset(df.columns):
    st.error(f"Excel file must contain these columns: {required_columns}")
    st.write("Columns found:", list(df.columns))
    st.stop()

df_agg = (
    df.groupby("Category", as_index=False)[value_cols]
      .sum()
)

df_agg["Category_clean"] = df_agg["Category"].astype(str).str.replace("_", " ", regex=False)
df_agg = df_agg[(df_agg[value_cols] > 0).any(axis=1)].copy()

if df_agg.empty:
    st.warning("No positive values found for Electricity, Fuel, or Steam.")
    st.stop()

base_palette = [
    "#A000FF",
    "#00D000",
    "#E00060",
    "#C6E000",
    "#C07030",
    "#3C7CFF",
    "#00B0FF",
    "#00C0A0",
    "#FF8000",
    "#FF00AA",
]

categories = df_agg["Category_clean"].tolist()
n_cat = len(categories)

palette = (base_palette * ((n_cat // len(base_palette)) + 1))[:n_cat]
color_map = dict(zip(categories, palette))

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
    row=1,
    col=1
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
    row=1,
    col=2
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
    row=1,
    col=3
)

fig.update_layout(
    title=dict(text="Unit Operation Level 2", x=0.5),
    paper_bgcolor="white",
    margin=dict(t=80, l=10, r=10, b=10),
    height=700
)

st.title("Figure 3")
st.plotly_chart(fig, use_container_width=True)
