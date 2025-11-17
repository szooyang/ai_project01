import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="지하철 승하차 분석", layout="wide")

st.title("🚇 2025년 10월 지하철 승하차 TOP10 분석 대시보드")

st.write("CSV 파일을 업로드해주세요. (예: subway.csv)")

uploaded_file = st.file_uploader("지하철 데이터 업로드", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="cp949")

    # 날짜 변환
    df["사용일자"] = pd.to_datetime(df["사용일자"].astype(str), format="%Y%m%d")

    # 사이드바 선택 UI
    st.sidebar.header("🔎 조건 선택")
    
    # 2025년 10월 날짜 범위
    start_date = pd.to_datetime("2025-10-01")
    end_date = pd.to_datetime("2025-10-31")

    selected_date = st.sidebar.date_input(
        "날짜 선택",
        min_value=start_date,
        max_value=end_date,
        value=start_date
    )

    # 선택한 날짜에 맞춰 필터링
    df_filtered_date = df[df["사용일자"] == pd.to_datetime(selected_date)]

    # 호선 선택
    lines = sorted(df_filtered_date["노선명"].unique())
    selected_line = st.sidebar.selectbox("호선 선택", lines)

    df_filtered = df_filtered_date[df_filtered_date["노선명"] == selected_line].copy()

    if df_filtered.empty:
        st.warning("해당 날짜와 호선에 대한 데이터가 없습니다.")
    else:
        # 승하차 합산
        df_filtered["승하차합"] = df_filtered["승차총승객수"] + df_filtered["하차총승객수"]

        # TOP 10 역 추출
        top10 = df_filtered.sort_values("승하차합", ascending=False).head(10)

        # 색상 설정 (1등 빨강, 나머지는 파랑→흐려지는 그라데이션)
        colors = ["red"] + [f"rgba(0,0,255,{1 - i*0.08})" for i in range(1, 10)]

        fig = px.bar(
            top10,
            x="역명",
            y="승하차합",
            title=f"🚇 {selected_date} / {selected_line} 승하차 합산 TOP10",
            text="승하차합"
        )

        fig.update_traces(marker_color=colors, textposition="outside")

        fig.update_layout(
            xaxis_title="역명",
            yaxis_title="승하차 승객수 합계",
            template="plotly_white",
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("지하철 CSV 파일을 먼저 업로드해주세요.")
