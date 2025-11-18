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

    # 일자(일) 컬럼 추가
    df["day"] = df["date"].dt.day

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
# 상/중/하 등급 계산 함수
# ---------------------------
def rank_to_level(value, series: pd.Series) -> str:
    """
    해당 값이 series 안에서 어느 정도 위치인지 보고
    상/중/하 등급으로 반환.
    - 상: 상위 1/3 이상
    - 중: 중간 1/3
    - 하: 하위 1/3
    """
    if series.empty:
        return "-"

    q1 = series.quantile(1/3)
    q2 = series.quantile(2/3)

    if value >= q2:
        return "상"
    elif value >= q1:
        return "중"
    else:
        return "하"


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

        아래에는 **역 이름으로 조회해서**  
        - 이 역이 **몇 호선인지**  
        - **월초 / 월중 / 월말** 기준으로 승·하차 평균  
        - 같은 호선에서 이 역의 **승·하차 규모가 상/중/하 중 어디쯤인지**  
        를 확인할 수 있는 기능도 있습니다.
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
    # 선택 조건에 따른 데이터 필터링 (그래프용)
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
    else:
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

        with st.expander("🔎 필터링된 원본 데이터(상위 20행) 보기"):
            st.dataframe(df_filtered.head(20))

    # ============================================================
    # 🚉 역 입력 받아서 정보 조회하는 섹션 (여기부터 추가된 부분)
    # ============================================================
    st.markdown("---")
    st.subheader("🚉 역 기준 상세 분석")

    # 역 목록 (오름차순)
    station_list = sorted(df["역명"].unique())

    selected_station = st.selectbox(
        "역을 선택하세요",
        options=station_list,
        index=0,
    )

    # 선택된 역에 대한 전체 (2025년 10월) 데이터
    df_station = df[df["역명"] == selected_station].copy()

    if df_station.empty:
        st.warning("선택한 역에 대한 데이터가 없습니다.")
        return

    # 이 역이 포함된 호선 목록
    lines_for_station = sorted(df_station["노선명"].unique())

    st.write(
        f"**{selected_station}역**은(는) 다음 호선에 포함되어 있습니다: "
        + ", ".join([f"**{ln}**" for ln in lines_for_station])
    )

    # ---------------------------
    # 월초 / 월중 / 월말 구간 정의
    # ---------------------------
    def period_label(day: int) -> str:
        if day <= 10:
            return "월초 (1~10일)"
        elif day <= 20:
            return "월중 (11~20일)"
        else:
            return "월말 (21~말일)"

    df_station["기간구분"] = df_station["day"].apply(period_label)

    # 기간별 승차/하차 평균
    period_avg = (
        df_station.groupby("기간구분")[["승차총승객수", "하차총승객수"]]
        .mean()
        .round(1)
        .reindex(["월초 (1~10일)", "월중 (11~20일)", "월말 (21~말일)"])
    )

    st.markdown("#### 📆 월초·월중·월말 승·하차 평균 (2025년 10월 기준)")
    st.dataframe(
        period_avg.rename(
            columns={
                "승차총승객수": "승차 평균",
                "하차총승객수": "하차 평균",
            }
        )
    )

    # ---------------------------
    # 같은 호선 내에서 상/중/하 등급 계산
    # ---------------------------
    st.markdown("#### 📊 같은 호선 내에서 이 역의 규모 (상/중/하)")

    grade_rows = []
    for line_name in lines_for_station:
        # 해당 호선 전체역 데이터
        df_line = df[df["노선명"] == line_name].copy()
        if df_line.empty:
            continue

        # 호선 내 역별 총 승차/하차 합계
        line_group = (
            df_line.groupby("역명")[["승차총승객수", "하차총승객수"]]
            .sum()
        )

        if selected_station not in line_group.index:
            continue

        station_totals = line_group.loc[selected_station]

        # 상/중/하 등급
        승차등급 = rank_to_level(
            station_totals["승차총승객수"],
            line_group["승차총승객수"],
        )
        하차등급 = rank_to_level(
            station_totals["하차총승객수"],
            line_group["하차총승객수"],
        )

        grade_rows.append(
            {
                "호선": line_name,
                "역명": selected_station,
                "총 승차 인원 (월합계)": int(station_totals["승차총승객수"]),
                "총 하차 인원 (월합계)": int(station_totals["하차총승객수"]),
                "승차 규모": 승차등급,
                "하차 규모": 하차등급,
            }
        )

    if not grade_rows:
        st.info("해당 역에 대한 호선별 비교 데이터를 계산할 수 없습니다.")
    else:
        grade_df = pd.DataFrame(grade_rows)
        st.dataframe(grade_df)


if __name__ == "__main__":
    main()
