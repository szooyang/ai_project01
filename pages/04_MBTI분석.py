import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="MBTI by Country - Plotly", layout="wide")

# -------- Data Loader --------
@st.cache_data(show_spinner=True)
def load_data(csv_path: str = "countriesMBTI_16types.csv"):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    mbti_cols = [
        "INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
        "ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
    ]
    expected = ["Country"] + mbti_cols
    cols_present = [c for c in expected if c in df.columns]
    df = df[cols_present].copy()
    for c in mbti_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["Country"]).reset_index(drop=True)
    return df

MBTI_ORDER = [
    "INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
    "ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
]

def build_colors(values: pd.Series):
    if values.empty:
        return []
    max_label = values.idxmax()
    others = values.drop(index=max_label)
    n = len(others)
    if n == 0:
        return ["crimson"]
    grad = np.linspace(0.25, 0.95, n)
    navy = np.array([0, 52, 130])
    blue = np.array([30, 144, 255])
    colors_map = {}
    for lbl, a in zip(others.index, grad):
        rgb = (1 - a) * blue + a * navy
        r, g, b = rgb.astype(int).tolist()
        colors_map[lbl] = f"rgba({r},{g},{b},1.0)"
    colors_map[max_label] = "crimson"
    return [colors_map[lbl] for lbl in values.index]

def plot_country_bars(row: pd.Series, sort_desc: bool = True):
    vals = row[MBTI_ORDER].astype(float)
    if sort_desc:
        vals = vals.sort_values(ascending=False)
    colors = build_colors(vals)
    fig = go.Figure(data=[
        go.Bar(
            x=list(vals.index),
            y=(vals.values * 100).round(2),
            marker=dict(color=colors),
            hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
        )
    ])
    fig.update_layout(
        title=dict(text="MBTI Distribution - " + str(row["Country"]), x=0.02, xanchor="left"),
        xaxis_title="MBTI Type",
        yaxis_title="Share (%)",
        bargap=0.25,
        height=520,
        margin=dict(l=30, r=20, t=60, b=40),
    )
    return fig

st.title("MBTI by Country (Plotly)")
st.caption("Top type is red, others are blue gradient.")

with st.expander("Data file help", expanded=False):
    st.write(
        "- Put countriesMBTI_16types.csv in the same folder as this app.\n"
        "- If the filename differs, change it below."
    )

csv_name = st.text_input("CSV filename", value="countriesMBTI_16types.csv")

try:
    df = load_data(csv_name)
except Exception as e:
    st.error("Error reading CSV: " + str(e))
    st.stop()

if "Country" not in df.columns:
    st.error("CSV must contain a 'Country' column.")
    st.stop()

countries = sorted(df["Country"].dropna().unique().tolist())
col1, col2 = st.columns([1.2, 2.8])
with col1:
    country = st.selectbox("Select country", countries, index=0)
    sort_desc = st.toggle("Sort by value (descending)", value=True, help="Recommended for readability")

with col2:
    sel_row = df.loc[df["Country"] == country].iloc[0]
    fig = plot_country_bars(sel_row, sort_desc=sort_desc)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("View data for selected country"):
    tbl = (
        sel_row[MBTI_ORDER]
        .astype(float)
        .rename("share")
        .mul(100)
        .round(2)
        .sort_values(ascending=not sort_desc)
        .to_frame()
    )
    st.dataframe(tbl, use_container_width=True)

with st.expander("Show app.py code for copy"):
    try:
        import os
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            st.code(f.read(), language="python")
    except Exception as e:
        st.info("Source code display may be restricted on this platform. Please open app.py in your repo.")
