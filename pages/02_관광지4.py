import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import random

st.set_page_config(page_title="서울 관광 일정 플래너", layout="wide")

st.title("🌏 외국인이 좋아하는 서울 주요 관광지 TOP 10")
st.markdown("서울의 대표 관광지 10곳을 한눈에 보고, 여행 일정을 자동으로 만들어보세요!")

# 관광지 데이터
attractions = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, 
     "desc": "조선의 대표 궁궐로, 아름다운 건축미와 근정전, 경회루가 유명합니다.", 
     "subway": "3호선 경복궁역"},
    {"name": "북촌한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, 
     "desc": "전통 한옥이 잘 보존된 마을로, 한국의 옛 정취를 느낄 수 있습니다.", 
     "subway": "3호선 안국역"},
    {"name": "인사동 (Insadong)", "lat": 37.574012, "lon": 126.984955, 
     "desc": "전통 찻집, 공예품 상점이 즐비한 한국 문화 거리입니다.", 
     "subway": "3호선 안국역"},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982684, 
     "desc": "쇼핑과 길거리 음식이 유명한 서울의 번화가입니다.", 
     "subway": "4호선 명동역"},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, 
     "desc": "서울의 전경을 한눈에 볼 수 있는 전망대 명소입니다.", 
     "subway": "4호선 명동역"},
    {"name": "동대문디자인플라자 (Dongdaemun Design Plaza)", "lat": 37.566478, "lon": 127.009214, 
     "desc": "미래적인 디자인 건축물로, 전시와 문화행사가 자주 열립니다.", 
     "subway": "2·4·5호선 동대문역사문화공원역"},
    {"name": "홍대 (Hongdae)", "lat": 37.556334, "lon": 126.923597, 
     "desc": "젊음과 예술, 거리공연으로 유명한 활기찬 지역입니다.", 
     "subway": "2호선 홍대입구역"},
    {"name": "이태원 (Itaewon)", "lat": 37.534502, "lon": 126.994274, 
     "desc": "다양한 세계 음식을 즐길 수 있는 다문화 거리입니다.", 
     "subway": "6호선 이태원역"},
    {"name": "롯데월드 (Lotte World)", "lat": 37.51104, "lon": 127.09802, 
     "desc": "세계 최대 실내 놀이공원 중 하나로, 가족 관광객에게 인기가 높습니다.", 
     "subway": "2호선 잠실역"},
    {"name": "창덕궁 (Changdeokgung Palace)", "lat": 37.579414, "lon": 126.991058, 
     "desc": "유네스코 세계유산으로 등록된 궁궐로, 비원(후원)이 아름답습니다.", 
     "subway": "3호선 안국역"}
]

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="OpenStreetMap")

# 마커 클러스터 추가
marker_cluster = MarkerCluster().add_to(m)

# 마커 추가 (빨간색 아이콘)
for spot in attractions:
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=f"<b>{spot['name']}</b><br>{spot['desc']}<br>🚇 {spot['subway']}",
        tooltip=spot["name"],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(marker_cluster)

# 지도 출력 (크기 축소)
st_data = st_folium(m, width=630, height=420)

# 관광지 설명 리스트
st.markdown("### 🗺️ 관광지 정보 요약")
for i, spot in enumerate(attractions, start=1):
    st.markdown(f"**{i}. {spot['name']}** — {spot['desc']}  \n🚇 **가까운 전철역:** {spot['subway']}")

# 여행 일정 생성기
st.markdown("---")
st.subheader("📅 여행 일정 만들기")

days = st.slider("여행 일수를 선택하세요 (1~3일)", min_value=1, max_value=3, value=2)

# 일정 생성 (10개 명소를 일수로 균등 분배)
spots_per_day = len(attractions) // days
random.shuffle(attractions)

for d in range(days):
    st.markdown(f"#### ✨ {d+1}일차 일정")
    start = d * spots_per_day
    end = (d + 1) * spots_per_day if d < days - 1 else len(attractions)
    for spot in attractions[start:end]:
        st.markdown(f"- {spot['name']}  \n  🚇 {spot['subway']}  \n  💬 {spot['desc']}")
