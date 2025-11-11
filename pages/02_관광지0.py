import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="서울 관광지 지도", layout="wide")

st.title("🗺️ 외국인들이 좋아하는 서울의 주요 관광지 Top 10")

# 서울 관광지 데이터
spots = [
    {"name": "경복궁", "lat": 37.579617, "lon": 126.977041, "station": "경복궁역", 
     "desc": "조선의 정궁으로, 아름다운 궁궐과 수문장 교대식으로 유명해요."},
    {"name": "명동", "lat": 37.563757, "lon": 126.982669, "station": "명동역", 
     "desc": "쇼핑과 맛집의 천국! 외국인 관광객이 가장 많이 찾는 거리예요."},
    {"name": "남산타워(N서울타워)", "lat": 37.551169, "lon": 126.988227, "station": "명동역", 
     "desc": "서울의 랜드마크로, 전망대에서 서울 전경을 한눈에 볼 수 있어요."},
    {"name": "홍대거리", "lat": 37.556327, "lon": 126.922051, "station": "홍대입구역", 
     "desc": "젊음과 예술의 거리로, 클럽·버스킹·카페로 활기찬 분위기를 즐길 수 있어요."},
    {"name": "이태원", "lat": 37.534539, "lon": 126.994941, "station": "이태원역", 
     "desc": "다양한 나라의 음식과 문화가 어우러진 글로벌 거리예요."},
    {"name": "북촌한옥마을", "lat": 37.582604, "lon": 126.983998, "station": "안국역", 
     "desc": "전통 한옥이 모여 있는 마을로, 한국의 옛 정취를 느낄 수 있어요."},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.566478, "lon": 127.009153, "station": "동대문역사문화공원역", 
     "desc": "미래형 건축물과 패션·디자인 전시로 유명한 복합 문화 공간이에요."},
    {"name": "잠실 롯데월드", "lat": 37.511028, "lon": 127.098152, "station": "잠실역", 
     "desc": "실내외 놀이공원과 쇼핑몰, 아쿠아리움까지 즐길 수 있는 종합 엔터테인먼트 공간이에요."},
    {"name": "코엑스몰", "lat": 37.512527, "lon": 127.058777, "station": "삼성역", 
     "desc": "아시아 최대 규모의 지하 쇼핑몰로, 별마당 도서관이 유명해요."},
    {"name": "청계천", "lat": 37.570052, "lon": 126.982247, "station": "광화문역", 
     "desc": "도심 속 휴식 공간으로, 산책하기 좋은 도심 하천이에요."}
]

# 지도 생성 (기본 배경 지도 스타일 유지)
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 관광지 마커 추가
for spot in spots:
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=None,  # 클릭 시 설명 안 보이게
        tooltip=f"{spot['name']} ({spot['station']})",  # 마우스 올리면 표시
        icon=folium.Icon(color="yellow", icon="info-sign")
    ).add_to(m)

# 지도 표시 (크기 80%)
st_folium(m, width=900, height=500)

# 관광지 설명 섹션
st.subheader("📍 관광지 소개")
for i, spot in enumerate(spots, 1):
    st.markdown(f"**{i}. {spot['name']}** ({spot['station']})  \n👉 {spot['desc']}")
