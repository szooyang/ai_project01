import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import requests
from folium.features import GeoJson

# 앱 설정
st.set_page_config(page_title="서울 관광지도", page_icon="🗺️", layout="wide")

st.title("🗺️ 외국인들이 좋아하는 서울의 주요 관광지 Top 10")
st.markdown("서울 지역만 강조된 지도에서 외국인들이 즐겨 찾는 명소를 확인해보세요! 🌏")

# 서울 관광지 데이터
spots = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "station": "경복궁역 (3호선)"},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982669, "station": "명동역 (4호선)"},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, "station": "명동역 (4호선)"},
    {"name": "북촌 한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, "station": "안국역 (3호선)"},
    {"name": "홍대 (Hongdae)", "lat": 37.556318, "lon": 126.922651, "station": "홍대입구역 (2호선, 경의중앙선)"},
    {"name": "인사동 (Insadong)", "lat": 37.574015, "lon": 126.985829, "station": "종로3가역 (1·3·5호선)"},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.513068, "lon": 127.102491, "station": "잠실역 (2·8호선)"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566479, "lon": 127.009190, "station": "동대문역사문화공원역 (2·4·5호선)"},
    {"name": "청계천 (Cheonggyecheon Stream)", "lat": 37.569308, "lon": 126.978998, "station": "종각역 (1호선)"},
    {"name": "잠실 롯데월드 (Lotte World)", "lat": 37.511000, "lon": 127.098000, "station": "잠실역 (2·8호선)"},
]

# Folium 지도 생성 (회색 지도)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="CartoDB positron")

# 서울 경계 데이터 (공공 데이터 GeoJSON 사용)
# 출처: https://github.com/southkorea/seoul-maps
url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/json/seoul_municipalities_geo_simple.json"
geojson = requests.get(url).json()

# 지도 배경은 회색, 서울만 강조
folium.GeoJson(
    geojson,
    style_function=lambda x: {
        "fillColor": "#f9d423",
        "color": "gray",
        "weight": 1,
        "fillOpacity": 0.5,
    },
    highlight_function=lambda x: {"fillColor": "#ffcc00", "fillOpacity": 0.7},
).add_to(m)

# 마커 추가 (노란색)
for spot in spots:
    tooltip_text = f"{spot['name']} 🚇 {spot['station']}"
    folium.Marker(
        [spot["lat"], spot["lon"]],
        tooltip=tooltip_text,
        icon=folium.Icon(color="orange", icon="info-sign"),
    ).add_to(m)

# 지도 출력 (80%)
st.markdown("### 🗺️ 서울 관광지도 (서울만 색 강조)")
st_folium(m, width=720, height=480)

# 관광지 소개
st.markdown("---")
st.markdown("### 📍 관광지 간단 소개")

for spot in spots:
    st.markdown(f"**{spot['name']}**  \n🚇 *가까운 역:* {spot['station']}  \n")

st.markdown("---")
st.caption("데이터 출처: 서울관광재단 · Visit Seoul · Github(seoul-maps)")
