# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os

st.set_page_config(page_title="연령별 인구 그래프", layout="wide")

st.title("지역별 연령대 인구 꺾은선 그래프 (Plotly + Streamlit)")

# --- 데이터 로드: 여러 인코딩 시도 ---
def load_csv_try(path_candidates):
    last_err = None
    for p in path_candidates:
        if not os.path.exists(p):
            continue
        for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
            try:
                df = pd.read_csv(p, encoding=enc)
                return df, p, enc
            except Exception as e:
                last_err = e
    raise RuntimeError(f"파일을 열 수 없습니다. 시도한 경로/인코딩 실패. 마지막 오류: {last_err}")

# 후보 경로: 앱 루트에 population.csv 두는 경우, 또는 /mnt/data (업로드 환경)
file_candidates = ["./population.csv", "./data/population.csv", "/mnt/data/population.csv", "population.csv"]
try:
    df_raw, used_path, used_encoding = load_csv_try(file_candidates)
except Exception as e:
    st.error("population.csv 파일을 찾지 못했거나 열 수 없습니다. 앱 디렉토리에 population.csv 파일을 올려주세요.")
    st.stop()

st.sidebar.markdown(f"**데이터 파일:** `{used_path}`  (인코딩: {used_encoding})")

# 작은 전처리: 칼럼 이름 공백 제거
df = df_raw.copy()
df.columns = [c.strip() for c in df.columns]

# 가능한 지역(행정구역) 컬럼 탐색
region_col_candidates = [c for c in df.columns if re.search(r"행정|시군구|지역|지역명|시군", c, re.I)]
if region_col_candidates:
    region_col = region_col_candidates[0]
else:
    # fallback: 첫번째 컬럼 사용
    region_col = df.columns[0]

# 가능한 '항목' or '연령' 컬럼 탐색
age_label_col_candidates = [c for c in df.columns if re.search(r"항목|연령|연령구간|구간|나이", c, re.I)]
age_label_col = age_label_col_candidates[0] if age_label_col_candidates else None

# 연도/시점 컬럼(숫자 형태 또는 YYYY 형태) 탐색
year_cols = [c for c in df.columns if re.match(r"^\d{4}(\.\d+)?$|^\d{4}년|^\d{4}년", str(c))]
# 추가: 컬럼명이 '2025년10월...' 같이 포함된 경우
year_like_cols = [c for c in df.columns if re.search(r"\d{4}", str(c)) and c not in [region_col, age_label_col]]
# 결합, 중복 제거
all_year_candidates = list(dict.fromkeys(year_cols + year_like_cols))

# UI: 지역 선택
regions = df[region_col].astype(str).unique().tolist()
regions_display = sorted([r for r in regions if r and str(r).strip()!=""], key=lambda x: str(x))
sel_region = st.sidebar.selectbox("지역 선택", regions_display)

# UI: 시점(연도) 선택
if all_year_candidates:
    sel_year = st.sidebar.selectbox("시점(연도/컬럼) 선택 (그래프에 쓸 인구값을 담은 컬럼)", all_year_candidates, index=len(all_year_candidates)-1)
else:
    sel_year = st.sidebar.text_input("직접 입력할 인구수 컬럼명 (예: 2024)", value="2024")

st.write(f"선택 지역: **{sel_region}**, 선택 시점 컬럼: **{sel_year}**")

# --- 데이터 준비 함수 ---
def clean_number(x):
    if pd.isna(x):
        return None
    if isinstance(x, (int, float)):
        return x
    s = str(x)
    # 숫자 바깥 문자 제거 (콤마, 공백, 괄호 등)
    s = re.sub(r"[^\d\-\.]", "", s)
    try:
        if s == "" or s == "-" :
            return None
        if "." in s:
            return float(s)
        return int(s)
    except:
        return None

def prepare_age_population(df, region, region_col, age_label_col, value_col):
    # 케이스 A: 세로형(각 행이 연령 항목) — age_label_col이 존재
    if age_label_col and age_label_col in df.columns and value_col in df.columns:
        sub = df[df[region_col].astype(str) == str(region)][[age_label_col, value_col]].copy()
        sub = sub.rename(columns={age_label_col: "age_label", value_col: "pop"})
        sub["pop"] = sub["pop"].apply(clean_number)
        sub = sub.dropna(subset=["pop"])
        return sub
    # 케이스 B: 연령이 컬럼명인 가로형 (예: '0세','1세', ... 가 여러 컬럼)
    age_like_cols = [c for c in df.columns if re.search(r"^\d+세$|^\d+-\d+|^\d+~\d+|^\d+대", str(c))]
    # also try columns that look numeric or small ints
    if not age_like_cols:
        # 추정: 첫행이 지역별 전체 인구 행이고, 연령 컬럼들이 아닌가
        # 시도: 선택한 지역의 row에서 숫자형으로 변환 가능한 컬럼들 추출
        row = df[df[region_col].astype(str) == str(region)]
        if not row.empty:
            possible_cols = []
            for c in df.columns:
                if c==region_col: continue
                v = row.iloc[0].get(c)
                if pd.isna(v): continue
                cleaned = re.sub(r"[^\d\-\.]", "", str(v))
                if cleaned:
                    possible_cols.append(c)
            # 정렬(가능하면 연령 순)
            age_like_cols = possible_cols
    if age_like_cols:
        row = df[df[region_col].astype(str) == str(region)]
        if row.empty:
            return pd.DataFrame(columns=["age_label","pop"])
        row = row.iloc[0]
        records = []
        for c in age_like_cols:
            val = clean_number(row.get(c))
            if val is None:
                continue
            records.append({"age_label": str(c), "pop": val})
        if records:
            return pd.DataFrame(records)
    # 실패 시: 빈 데이터 반환
    return pd.DataFrame(columns=["age_label","pop"])

# 실제 준비
data_agepop = prepare_age_population(df, sel_region, region_col, age_label_col, sel_year)

if data_agepop.empty:
    st.warning("선택한 형식에서 연령별 인구 데이터를 찾지 못했습니다. 데이터 예시를 아래에서 확인하고, '시점(연도) 선택'을 올바른 컬럼명으로 바꿔보세요.")
    st.subheader("데이터 파일(앞부분) 미리보기")
    st.dataframe(df.head(30))
    st.stop()

# 연령 라벨 정렬 시도: 숫자 추출해서 정렬
def age_key(label):
    # extract first integer in label
    m = re.search(r"(\d{1,3})", str(label))
    if m:
        return int(m.group(1))
    # fallback: length-based
    return str(label)

data_agepop["age_sort"] = data_agepop["age_label"].apply(age_key)
data_agepop = data_agepop.sort_values("age_sort").reset_index(drop=True)

# Plotly 라인
fig = px.line(data_agepop, x="age_label", y="pop", markers=True,
              title=f"{sel_region} - 연령별 인구 ({sel_year})",
              labels={"age_label":"연령(또는 연령구간)", "pop":"인구수"})
fig.update_layout(xaxis_tickangle= -45)
fig.update_traces(hovertemplate="%{x}<br>인구: %{y:,}")

# Show chart and table
st.plotly_chart(fig, use_container_width=True)

with st.expander("데이터 테이블 보기"):
    st.dataframe(data_agepop[["age_label","pop"]].rename(columns={"age_label":"연령","pop":"인구수"}))

# 간단한 통계
st.markdown("**요약 통계(표본)**")
st.write(data_agepop["pop"].describe().apply(lambda x: f"{x:,}" if pd.notna(x) else x).to_frame().T)

# CSV로 다운로드 링크 제공
@st.cache_data
def df_to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8-sig')

csv_bytes = df_to_csv_bytes(data_agepop[["age_label","pop"]].rename(columns={"age_label":"연령","pop":"인구수"}))
st.download_button("연령별 인구 CSV 다운로드", data=csv_bytes, file_name=f"{sel_region}_agepop_{sel_year}.csv", mime="text/csv")

st.info("문제가 있거나 특정 형식(예: 연령이 행으로 있을 때, 또는 특정 컬럼명이 있을 때)로 맞춰서 더 튜닝하길 원하면 데이터 파일의 앞부분(예시 10행)을 붙여서 알려주세요.")
