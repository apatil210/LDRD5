import streamlit as st
import pandas as pd
import plotly.express as px
import colorsys
import requests
from io import BytesIO

st.set_page_config(page_title="Figure 2", layout="wide")

file_url = "https://raw.githubusercontent.com/apatil210/LDRD/main/Figure2Data.xlsx"


@st.cache_data
def load_data(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_excel(BytesIO(response.content), engine="openpyxl")


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
    title=dict(text="Unit Operation Level 2", x=0.5),
    paper_bgcolor="white",
    margin=dict(t=70, l=10, r=10, b=10)
)

st.title("Figure 2")
st.plotly_chart(fig, use_container_width=True)
