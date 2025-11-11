import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import inspect


st.set_page_config(page_title="MBTI by Country • Plotly", page_icon="🧭", layout="wide")


# -------------------------------
# Data Loader (cached)
# -------------------------------
@st.cache_data(show_spinner=True)
def load_data(csv_path: str = "countriesMBTI_16types.csv"):
df = pd.read_csv(csv_path, encoding="utf-8-sig")
# Keep only expected columns if present
mbti_cols = [
"INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
"ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
]
expected = ["Country"] + mbti_cols
cols_present = [c for c in expected if c in df.columns]
df = df[cols_present].copy()


# Coerce numeric types
for c in mbti_cols:
if c in df.columns:
df[c] = pd.to_numeric(df[c], errors="coerce")


df = df.dropna(subset=["Country"]).reset_index(drop=True)
return df


# -------------------------------
# Utilities
# -------------------------------
MBTI_ORDER = [
"INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
"ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
]


def build_colors(values: pd.Series):
"""Top-1 in red, others in blue gradient."""
if values.empty:
return []
# Index label (MBTI) of max value
st.caption("Built with Streamlit • Plotly • pandas • numpy")
