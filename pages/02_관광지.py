import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="서울 외국인 인기 관광지 Top10", layout="wide")

st.title("🌏 외국인이 좋아하는 서울 관광지 Top10")
st.markdown("왼쪽에서 필터를 설정할 수 있어요! 마커를 클릭하면 정보를 볼 수 있어요.")

# 서울 인기 관광지 데이터 (이름, 위도, 경도, 설명, 링크)
TOP10 = [
    {
        "name": "경복궁",
        "lat": 37.579617,
        "lon": 126.977041,
        "desc": "조선 시대의 법궁, 한국을 대표하는 궁궐.",
        "link": "https://ko.wikipedia.org/wiki/경복궁",
    },
    {
        "name": "북촌 한옥마을",
        "lat": 37.582604,
        "lon": 126.983059,
        "desc": "전통 한옥이 보존된 아름다운 마을.",
        "link": "https://ko.wikipedia.org/wiki/북촌_한옥마을",
    },
    {
        "name": "남산 / N서울타워",
        "lat": 37.5511694,
        "lon": 126.9882266,
        "desc": "서울의 랜드마크, 전망이 훌륭한 타워.",
        "link": "https://ko.wikipedia.org/wiki/N서울타워",
    },
    {
        "name": "명동 쇼핑거리",
        "lat": 37.563757,
        "lon": 126.986124,
        "desc": "외국인에게 가장 유명한 쇼핑, 먹거리 지역.",
        "link": "https://ko.wikipedia.org/wiki/명동",
    },
    {
        "name": "인사동",
        "lat": 37.574097,
        "lon": 126.985156,
        "desc": "전통 문화와 공예, 찻집이 많은 거리.",
        "link": "https://ko.wikipedia.org/wiki/인사동",
    },
    {
        "name": "홍대거리",
        "lat": 37.556230,
        "lon": 126.923941,
        "desc": "젊음의 거리! 공연, 카페, 쇼핑, 예술문화 중심.",
        "link": "https://ko.wikipedia.org/wiki/홍대",
    },
    {
        "name": "동대문디자인플라자(DDP)",
        "lat": 37.5662952,
        "lon": 127.0090436,
        "desc": "독특한 디자인과 야경이 멋진 건축 명소.",
        "link": "https://ko.wikipedia.org/wiki/동대문디자인플라자",
    },
    {
        "name": "롯데월드타워 & 몰",
        "lat": 37.513087,
        "lon": 127.101257,
        "desc": "전망대, 쇼핑, 공연 등 종합 엔터테인먼트.",
        "link": "https://ko.wikipedia.org/wiki/롯데월드타워",
    },
    {
        "name": "창덕궁 & 후원",
        "lat": 37.579529,
        "lon": 126.991020,
        "desc": "UNESCO 세계유산, 자연과 조화로운 궁궐.",
        "link": "https://ko.wikipedia.org/wiki/창덕궁",
    },
    {
        "name": "스타필드 코엑스몰(강남)",
        "lat": 37.512070,
        "lon": 127.058556,
        "desc": "대형 쇼핑몰과 유명한 별마당 도서관.",
        "link": "https://ko.wikipedia.org/wiki/코엑스",
    },
]

# 사이드바
st.sidebar.header("🔍 설정")
show_cluster = st.sidebar.checkbox("마커 클러스터 사용", value=True)
search_place = st.sidebar.text_input("🔎 장소 검색 (Enter 입력)")
selected_place = st.sidebar.selectbox("📌 특정 장소 이동", options=["전체"] + [p["name"] for p in TOP10])

# 검색 기능
if search_place:
    filtered = [p for p in TOP10 if search_place.lower() in p["name"].lower()]
else:
    filtered = TOP10.copy()

# 특정 장소 선택 시 필터링
if selected_place != "전체":
    filtered = [p for p in TOP10 if p["name"] == selected_place]

# 지도
seoul_center = [37.5665, 126.9780]
m = folium.Map(location=seoul_center, zoom_start=12)

if show_cluster:
    marker_cluster = MarkerCluster().add_to(m)

# 지도에 관광지 표시
for idx, place in enumerate(filtered, start=1):
    popup_html = f"<b>{place['name']}</b><br>{place['desc']}<br><a href='{place['link']}' target='_blank'>자세히 보기</a>"
    marker = folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=popup_html,
        tooltip=f"{idx}. {place['name']}"
    )
    if show_cluster:
        marker.add_to(marker_cluster)
    else:
        marker.add_to(m)

# 특정 장소 선택 시 지도 위치 조정
if selected_place != "전체" and filtered:
    m.location = [filtered[0]["lat"], filtered[0]["lon"]]
    m.zoom_start = 15

# 지도 출력
st_folium(m, width=900, height=600)

# Top10 목록 출력
st.subheader("📍 관광지 목록")
cols = st.columns(2)
for i, place in enumerate(TOP10):
    with cols[i % 2]:
        st.markdown(f"**{i+1}. {place['name']}**")
        st.write(place["desc"])
        st.markdown(f"[자세히 보기]({place['link']})")

st.markdown("---")
st.caption("※ 데이터 출처: 서울을 방문한 외국인 관광객들에게 인기 있는 장소 기준으로 구성")
