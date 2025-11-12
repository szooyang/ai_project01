
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="인구 연령별 그래프", layout="wide")
st.title("행정구 선택 → 연령-인구 꺾은선 그래프")
st.caption("CSV: population.csv (상위 폴더), 인코딩 자동 감지(cp949/euc-kr/utf-8-sig)")

# ====== 데이터 로딩 ======
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    # pages/ 하위에서 상위 폴더의 population.csv 경로 추적
    candidate_paths = [
        Path(__file__).resolve().parent.parent / "population.csv",  # ../population.csv
        Path(__file__).resolve().parent / "population.csv",         # ./population.csv (fallback)
        Path("population.csv").resolve(),                           # CWD 기준
    ]

    csv_path = None
    for p in candidate_paths:
        if p.exists():
            csv_path = p
            break

    if csv_path is None:
        st.stop()

    last_error = None
    for enc in ["cp949", "euc-kr", "utf-8-sig"]:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            return df
        except Exception as e:
            last_error = e
    st.error(f"CSV 로딩 실패: {last_error}")
    st.stop()


df = load_data()

# ====== 컬럼 파싱 ======
# 예시 컬럼: '2025년10월_계_총인구수', '2025년10월_계_0세', '2025년10월_계_100세 이상'
# 사용 가능한 최신(또는 임의의 하나) 접두어(YYYY년M월_계_)를 자동 탐색
prefix_pattern = re.compile(r"^(\d{4}년\d{1,2}월)_계_")

prefix_counts = {}
for c in df.columns:
    m = prefix_pattern.match(str(c))
    if m:
        prefix_counts[m.group(1)] = prefix_counts.get(m.group(1), 0) + 1

if not prefix_counts:
    st.error("연령/성별 인구 컬럼을 찾지 못했습니다. (예: 2025년10월_계_0세)")
    st.stop()

# 가장 많은 컬럼을 가진 접두어를 사용 (보통 최신 월)
selected_yearmonth = max(prefix_counts, key=prefix_counts.get)
base_prefix = f"{selected_yearmonth}_계_"

# 나이 컬럼만 수집 (총인구수 제외)
age_cols = []
for c in df.columns:
    if str(c).startswith(base_prefix):
        suffix = str(c).replace(base_prefix, "")
        if suffix == "총인구수":
            continue
        age_cols.append(str(c))

# 0세~99세, 그리고 '100세 이상' 둘로 분리해 숫자 키 생성
ages = []  # (age_int, colname)
for col in age_cols:
    suffix = col.replace(base_prefix, "")
    if suffix.endswith("세 이상"):
        age_int = 100
    else:
        try:
            age_int = int(suffix.replace("세", ""))
        except ValueError:
            continue
    ages.append((age_int, col))

# 나이순 정렬
ages.sort(key=lambda x: x[0])

# 행정구역 선택 박스
region_col = "행정구역"
if region_col not in df.columns:
    st.error("'행정구역' 컬럼을 찾을 수 없습니다.")
    st.stop()

regions = df[region_col].astype(str).tolist()
selected_region = st.selectbox("행정구역을 선택하세요", regions, index=0)

row = df[df[region_col].astype(str) == selected_region]
if row.empty:
    st.warning("선택한 행정구역의 데이터가 없습니다.")
    st.stop()
row = row.iloc[0]

# 값 정수 변환 함수 (쉼표 제거 후 정수)
def to_int(val):
    if pd.isna(val):
        return np.nan
    s = str(val).replace(",", "").strip()
    if s == "":
        return np.nan
    try:
        return int(s)
    except Exception:
        return np.nan

age_list = []
value_list = []
for age, col in ages:
    value_list.append(to_int(row[col]))
    age_list.append(age)

# NaN 제거 처리 (있다면)
age_arr = np.array(age_list)
val_arr = np.array(value_list, dtype=float)
mask = ~np.isnan(val_arr)
age_arr = age_arr[mask]
val_arr = val_arr[mask]

# ====== 그래프 설정: 회색 배경, X축 10살 간격, Y축 100 단위 ======
fig, ax = plt.subplots(figsize=(12, 6))

# 배경색
ax.set_facecolor("#f0f0f0")
fig.patch.set_facecolor("#f0f0f0")

# 선 그리기
ax.plot(age_arr, val_arr, marker="o", linewidth=2)

# 축/눈금
ax.set_xlabel("나이(세)")
ax.set_ylabel("인구수(명)")
ax.set_title(f"{selected_region} · {selected_yearmonth} · 연령-인구 꺾은선")

# X축: 0~100세, 10살 단위
ax.set_xlim(0, 100)
ax.set_xticks(np.arange(0, 101, 10))

# Y축: 100 단위 (요청 사항). 최대값에 맞춰 범위/눈금 자동 계산.
if len(val_arr) and np.isfinite(val_arr).any():
    vmax = np.nanmax(val_arr)
    step = 100  # 요구사항: 100 단위 구분선
    upper = int(np.ceil(vmax / step) * step)
    ax.set_ylim(0, max(upper, step))
    ax.set_yticks(np.arange(0, max(upper, step) + step, step))

# 그리드: 주요 눈금만, 약간 옅게
ax.grid(which="major", linestyle="-", alpha=0.4)

# Y축 3자리 콤마
ax.get_yaxis().set_major_formatter(lambda x, pos: f"{int(x):,}")

st.pyplot(fig, use_container_width=True)

# 데이터 테이블(선택사항)
with st.expander("원자료 보기"):
    table_df = pd.DataFrame({"나이(세)": age_arr, "인구수(명)": val_arr.astype(int)})
    st.dataframe(table_df, use_container_width=True)

