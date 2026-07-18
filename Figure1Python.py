import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import BytesIO
from matplotlib.colors import to_rgb, to_hex
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(page_title="Figure 1", layout="wide")

base_color = "#474646"
light_factor = 0.001
file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure1Data.xlsx"


def make_shades(base_color, n, light_factor=0.25):
    rgb = np.array(to_rgb(base_color))
    light_rgb = 1 - (1 - rgb) * light_factor
    return [
        to_hex(light_rgb + (rgb - light_rgb) * t)
        for t in np.linspace(1, 0, n)
    ]


@st.cache_data
def load_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


try:
    df = load_data(file_url)
except Exception as e:
    st.error(f"Failed to load Excel file: {e}")
    st.stop()

required_columns = {"Category", "Data"}
if not required_columns.issubset(df.columns):
    st.error(f"Excel file must contain these columns: {required_columns}")
    st.write("Columns found:", list(df.columns))
    st.stop()

df_agg = (
    df.groupby("Category", as_index=False)["Data"]
      .sum()
)

df_agg = df_agg[df_agg["Data"] > 0].copy()
df_agg = df_agg.sort_values("Data", ascending=False).reset_index(drop=True)

if df_agg.empty:
    st.warning("No positive data values found after aggregation.")
    st.stop()

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
    row=1,
    col=1
)

fig.add_trace(
    go.Bar(
        x=categories,
        y=values,
        marker=dict(color=colors, line=dict(color="black", width=1)),
        hovertemplate="%{x}<br>%{y:.1%}<extra></extra>"
    ),
    row=2,
    col=1
)

fig.update_yaxes(range=[0.19, 0.20], tickformat=".0%", row=1, col=1)
fig.update_yaxes(range=[0.00, 0.05], tickformat=".0%", row=2, col=1)

fig.update_xaxes(showticklabels=False, row=1, col=1)
fig.update_xaxes(showticklabels=True, tickangle=45, row=2, col=1)

fig.update_layout(
    height=700,
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=40, b=40, l=60, r=30)
)

st.title("Figure 1")
st.plotly_chart(fig, use_container_width=True)
