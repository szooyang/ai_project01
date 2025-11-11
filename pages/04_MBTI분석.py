
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="MBTI by Country • Plotly", page_icon="🧭", layout="wide")

# -------------------------------
# Data Loader (cached)
# -------------------------------
@st.cache_data(show_spinner=True)
def load_data(csv_path: str = "countriesMBTI_16types.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Basic sanity: keep only MBTI columns + Country
    mbti_cols = [
        "INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
        "ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
    ]
    expected = ["Country"] + mbti_cols
    # If columns are not exactly matching, try to coerce/capitalize
    df = df[[c for c in expected if c in df.columns]]
    # Ensure dtypes
    for c in mbti_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Drop any rows with missing Country or all-NA MBTI
    df = df.dropna(subset=["Country"]).reset_index(drop=True)
    return df

# -------------------------------
# Utilities
# -------------------------------
MBTI_ORDER = [
    "INFJ","ISFJ","INTP","ISFP","ENTP","INFP","ENTJ",
    "ISTP","INTJ","ESFP","ESTJ","ENFP","ESTP","ISTJ","ENFJ","ESFJ"
]

def build_colors(values: pd.Series) -> list:
    """Color the highest bar in red, others in blue gradient.
    The gradient is computed by rank (descending) among non-top entries.
    """
    if len(values) == 0:
        return []
    # Index of max value
    max_idx = int(values.values.argmax())
    # Build gradient for others
    n = len(values) - 1
    # Avoid division by zero
    if n <= 0:
        return ["crimson"]

    # Light→Dark blue gradient by rank order among non-top
    # We'll assign gradient intensities 0..1 across remaining bars using np.linspace
    gradient = np.linspace(0.25, 0.95, n)  # lighter to darker

    # Helper to make rgba blue from intensity
    def blue_rgba(alpha: float) -> str:
        # base blue ~ dodgerblue (30,144,255), keep alpha full and vary brightness via blending
        # we'll convert intensity into a slightly darker RGB by mixing with navy (0, 52, 130)
        navy = np.array([0, 52, 130])
        blue = np.array([30, 144, 255])
        rgb = (1 - alpha) * blue + alpha * navy
        r, g, b = rgb.astype(int).tolist()
        return f"rgba({r},{g},{b},1.0)"

    colors = []
    grad_iter = iter(gradient)
    for i in range(len(values)):
        if i == max_idx:
            colors.append("crimson")  # top-1 red
        else:
            colors.append(blue_rgba(next(grad_iter)))
    return colors


def plot_country_bars(row: pd.Series, sort_desc: bool = True) -> go.Figure:
    # Extract MBTI values
    vals = row[MBTI_ORDER].astype(float)
    # Optionally sort for readability
    if sort_desc:
        vals = vals.sort_values(ascending=False)

    colors = build_colors(vals)

    fig = go.Figure(
        data=[
            go.Bar(
                x=vals.index.tolist(),
                y=(vals.values * 100).round(2),  # percentage
                marker=dict(color=colors),
                hovertemplate="<b>%{x}</b><br>%{y:.2f}%<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text=f"MBTI Distribution • {row['Country']}", x=0.02, xanchor="left"),
        xaxis_title="MBTI Type",
        yaxis_title="Share (%)",
        bargap=0.25,
        height=520,
        margin=dict(l=30, r=20, t=60, b=40),
    )
    return fig

# -------------------------------
# UI
# -------------------------------
st.title("MBTI by Country (Plotly)")
st.caption("Select a country to visualize its MBTI distribution. Top type is **red**, others are **blue gradient**.")

csv_default = "countriesMBTI_16types.csv"
# Info box / hint
with st.expander("📦 데이터 파일 안내", expanded=False):
    st.write(
        """
        - 앱과 같은 폴더에 **`countriesMBTI_16types.csv`** 파일을 두세요.
        - 파일명이 다르면 아래 입력칸에서 직접 파일명을 바꾸세요.
        """
    )

csv_name = st.text_input("CSV 파일명", value=csv_default, help="레포 내 CSV 파일명을 입력하세요.")

# Load
try:
    df = load_data(csv_name)
except Exception as e:
    st.error(f"CSV를 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

# Country selector
countries = df["Country"].dropna().sort_values().tolist()
col1, col2 = st.columns([1.2, 2.8])
with col1:
    country = st.selectbox("국가 선택", countries, index=0)
    sort_desc = st.toggle("값 내림차순 정렬", value=True, help="가독성을 위해 권장")

# Draw chart
with col2:
    sel_row = df.loc[df["Country"] == country].iloc[0]
    fig = plot_country_bars(sel_row, sort_desc=sort_desc)
    st.plotly_chart(fig, use_container_width=True)

# Summary table (optional)
with st.expander("📋 데이터 보기 (선택 국가)"):
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

# -------------------------------
# Show code for easy copy
# -------------------------------
with st.expander("📄 이 앱 코드 보기 (app.py)"):
    try:
        code_text = Path(__file__).read_text(encoding="utf-8")
        st.code(code_text, language="python")
    except Exception:
        st.info("로컬 환경에서는 소스코드 표시가 제한될 수 있습니다. 레포의 app.py를 확인하세요.")

with st.expander("📦 requirements.txt 예시"):
    st.code("""\
streamlit==1.40.0
pandas==2.2.3
plotly==5.24.1
numpy==2.1.2
""", language="text")

st.caption("Built with Streamlit • Plotly • pandas • numpy")
```

