import pathlib
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date

# ---------------------------
# 데이터 로딩 함수 (캐시 적용)
# ---------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    # 현재 파일 기준으로 상위 폴더에 있는 subway.csv 읽기
    csv_path = pathlib.Path(__file__).resolve().parent.parent / "subway.csv"

    # 인코딩 에러 대비해서 cp949 / utf-8-sig 순차 시도
    for enc in ["cp949", "utf-8-sig"]:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    # 날짜 컬럼을 datetime으로 변환
    df["date"] = pd.to_datetime(df["사용일자"].astype(str), format="%Y%m%d")

    # 2025년 10월 데이터만 필터링
    df = df[(df["date"].dt.year == 2025) & (df["date"].dt.month == 10)].copy()

    # 총 승하차 인원 컬럼 추가 (승차 + 하차)
    df["총승하차"] = df["승차총승객수"] + df["하차총승객수"]

    return df


# ---------------------------
# 파란색 그라데이션 색 생성 함수
# ---------------------------
def generate_blue_gradient(n: int):
    """
    n개의 파란색 계열 그라데이션 색상을 생성.
    진한 파란색 → 연한 하늘색으로 점점 밝아짐.
    """
    if n <= 0:
        return []

    start = (0, 90, 255)     # 진한 파란색
    end = (180, 220, 255)    # 아주 연한 하늘색

    colors = []
    for i in range(n):
        ratio = i / (n - 1) if n > 1 else 0
        r = int(start[0] + (end[0] - start[0]) * ratio)
        g = int(start[1] + (end[1] - start[1]) * ratio)
        b = int(start[2] + (end[2] - start[2]) * ratio)
        colors.append(f"#{r:02X}{g:02X}{b:02X}")
    return colors


# ---------------------------
# 메인 앱
# ---------------------------
def main():
    st.set_page_config(
        page_title="지하철 이용 현황 분석 (2025년 10월)",
        layout="wide",
    )

    st.title("🚇 지하철 이용 현황 분석 (2025년 10월)")
    st.markdown(
        """
        2025년 10월 중 **하루**와 **호선**을 선택하면  
        해당 조건에서 **승차 + 하차 인원이 가장 많은 역 순서**로 막대그래프를 보여줍니다.
        """
    )

    # 데이터 로딩
    df = load_data()

    if df.empty:
        st.error("2025년 10월 데이터가 없습니다. subway.csv를 다시 확인해주세요.")
        return

    # ---------------------------
    # 사이드바 필터 UI
    # ---------------------------
    st.sidebar.header("⚙️ 조건 선택")

    # 사용 가능한 날짜(2025년 10월) 목록
    available_dates = sorted(df["date"].dt.date.unique())
    default_date = available_dates[0] if available_dates else date(2025, 10, 1)

    selected_date = st.sidebar.selectbox(
        "날짜 선택 (2025년 10월)",
        options=available_dates,
        index=available_dates.index(default_date) if default_date in available_dates else 0,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
    )

    # 사용 가능한 노선 목록
    available_lines = sorted(df["노선명"].unique())
    selected_line = st.sidebar.selectbox(
        "호선 선택",
        options=available_lines,
        index=0,
    )

    st.sidebar.info(
        f"선택된 날짜: **{selected_date.strftime('%Y-%m-%d')}**\n\n"
        f"선택된 노선: **{selected_line}**"
    )

    # ---------------------------
    # 선택 조건에 따른 데이터 필터링
    # ---------------------------
    mask = (df["date"].dt.date == selected_date) & (df["노선명"] == selected_line)
    df_filtered = df[mask].copy()

    st.subheader("📄 선택 조건 요약")
    st.write(
        f"- 날짜: **{selected_date.strftime('%Y-%m-%d')}**  \n"
        f"- 노선: **{selected_line}**  \n"
        f"- 데이터 건수: **{len(df_filtered)}행**"
    )

    if df_filtered.empty:
        st.warning("선택한 날짜와 호선에 해당하는 데이터가 없습니다.")
        return

    # 역별 총 승하차 인원 집계
    df_grouped = (
        df_filtered.groupby("역명", as_index=False)["총승하차"]
        .sum()
        .sort_values("총승하차", ascending=False)
    )

    # ---------------------------
    # Plotly 막대그래프 생성
    # ---------------------------
    st.subheader("🏆 역별 승·하차 합계 (내림차순)")

    # 1등은 빨간색, 나머지는 파란색 → 하늘색 그라데이션
    n = len(df_grouped)
    if n > 0:
        blue_grad = generate_blue_gradient(max(n - 1, 0))
        colors = ["#FF0000"] + blue_grad  # 1등 빨간색
    else:
        colors = []

    fig = px.bar(
        df_grouped,
        x="역명",
        y="총승하차",
        text="총승하차",
    )

    # 각 막대 색상 적용
    fig.update_traces(
        marker_color=colors,
        texttemplate="%{text:,}",
        hovertemplate="<b>%{x}</b><br>총 승하차 인원: %{y:,}명<extra></extra>",
    )

    fig.update_layout(
        xaxis_title="역명",
        yaxis_title="총 승하차 인원 (명)",
        xaxis_tickangle=-45,
        margin=dict(l=40, r=20, t=40, b=120),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # 원본 데이터 일부 보기
    # ---------------------------
    with st.expander("🔎 필터링된 원본 데이터(상위 20행) 보기"):
        st.dataframe(df_filtered.head(20))


if __name__ == "__main__":
    main()
