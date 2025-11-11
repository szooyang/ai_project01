import streamlit as st
import folium
from streamlit_folium import st_folium

# 앱 설정
st.set_page_config(page_title="서울 관광지도", page_icon="🗺️", layout="wide")

st.title("🗺️ 외국인들이 좋아하는 서울의 주요 관광지 Top 10")
st.markdown("서울을 방문한 외국인들이 많이 찾는 관광 명소를 한눈에 볼 수 있는 지도입니다! 🌏")

# 서울 관광지 데이터
spots = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, 
     "station": "경복궁역 (3호선)", 
     "desc": "조선의 정궁으로 한국 전통 건축의 아름다움을 느낄 수 있어요."},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982669, 
     "station": "명동역 (4호선)", 
     "desc": "쇼핑과 길거리 음식으로 유명한 번화가입니다."},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, 
     "station": "명동역 (4호선)", 
     "desc": "서울 전경을 한눈에 볼 수 있는 전망 명소예요."},
    {"name": "북촌 한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, 
     "station": "안국역 (3호선)", 
     "desc": "전통 한옥이 모여 있는 아름다운 마을이에요."},
    {"name": "홍대 (Hongdae)", "lat": 37.556318, "lon": 126.922651, 
     "station": "홍대입구역 (2호선, 경의중앙선)", 
     "desc": "젊음과 예술의 거리로 활기찬 분위기가 매력적이에요."},
    {"name": "인사동 (Insadong)", "lat": 37.574015, "lon": 126.985829, 
     "station": "종로3가역 (1·3·5호선)", 
     "desc": "한국 전통 문화와 예술을 체험할 수 있는 거리예요."},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.513068, "lon": 127.102491, 
     "station": "잠실역 (2·8호선)", 
     "desc": "세계에서 가장 높은 빌딩 중 하나로 전망대가 멋져요."},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566479, "lon": 127.009190, 
     "station": "동대문역사문화공원역 (2·4·5호선)", 
     "desc": "미래적인 디자인으로 유명한 복합 문화공간이에요."},
    {"name": "청계천 (Cheonggyecheon Stream)", "lat": 37.569308, "lon": 126.978998, 
     "station": "종각역 (1호선)", 
     "desc": "도심 속에서 휴식을 즐길 수 있는 산책로예요."},
    {"name": "잠실 롯데월드 (Lotte World)", "lat": 37.511000, "lon": 127.098000, 
     "station": "잠실역 (2·8호선)", 
     "desc": "실내외 놀이시설이 있는 서울의 대표 테마파크예요."},
]

# 지도 생성 (색상 포함)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="OpenStreetMap")

# 마커 추가 (노란색)
for spot in spots:
    popup_html = f"<b>{spot['name']}</b><br>{spot['desc']}<br><i>🚇 {spot['station']}</i>"
    folium.Marker(
        [spot["lat"], spot["lon"]],
        tooltip=spot["name"],
        popup=popup_html,
        icon=folium.Icon(color="orange", icon="info-sign"),
    ).add_to(m)

# 지도 표시 (80% 크기)
st.markdown("### 🗺️ 서울 관광지도")
st_folium(m, width=720, height=480)

# 관광지 소개 섹션
st.markdown("---")
st.markdown("### 📍 관광지 간단 소개")

for spot in spots:
    st.markdown(f"**{spot['name']}**  \n🚇 *가까운 역:* {spot['station']}  \n📝 {spot['desc']}  \n")

st.markdown("---")
st.caption("데이터 출처: 서울관광재단 · Visit Seoul · Tripadvisor")
