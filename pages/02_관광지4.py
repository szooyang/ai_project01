import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Seoul Top 10 Attractions", layout="wide")

st.title("🌏 외국인이 좋아하는 서울 주요 관광지 TOP 10")
st.markdown("이 지도는 서울의 인기 관광지를 Folium으로 시각화합니다. (영문/한글 병기)")

# 관광지 데이터
attractions = [
    {"name": "Gyeongbokgung Palace (경복궁)", "lat": 37.579617, "lon": 126.977041, "desc": "Historic royal palace and symbol of Seoul."},
    {"name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.582604, "lon": 126.983998, "desc": "Traditional Korean houses in a scenic area."},
    {"name": "Insadong (인사동)", "lat": 37.574012, "lon": 126.984955, "desc": "Cultural street filled with tea houses and craft shops."},
    {"name": "Myeongdong (명동)", "lat": 37.563757, "lon": 126.982684, "desc": "Shopping and street food paradise."},
    {"name": "N Seoul Tower (남산타워)", "lat": 37.551169, "lon": 126.988227, "desc": "Observation tower offering panoramic city views."},
    {"name": "Dongdaemun Design Plaza (동대문디자인플라자)", "lat": 37.566478, "lon": 127.009214, "desc": "Futuristic architecture and design hub."},
    {"name": "Hongdae (홍대)", "lat": 37.556334, "lon": 126.923597, "desc": "Trendy area known for art, cafes, and nightlife."},
    {"name": "Itaewon (이태원)", "lat": 37.534502, "lon": 126.994274, "desc": "International district with global cuisine and nightlife."},
    {"name": "Lotte World (롯데월드)", "lat": 37.51104, "lon": 127.09802, "desc": "One of the world's largest indoor theme parks."},
    {"name": "Changdeokgung Palace (창덕궁)", "lat": 37.579414, "lon": 126.991058, "desc": "UNESCO World Heritage Site with a secret garden."}
]

# Folium 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="CartoDB positron")

# 마커 클러스터 추가
marker_cluster = MarkerCluster().add_to(m)

for spot in attractions:
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=f"<b>{spot['name']}</b><br>{spot['desc']}",
        tooltip=spot["name"]
    ).add_to(marker_cluster)

# 지도 표시
st_data = st_folium(m, width=900, height=600)

# 코드 표시
with st.expander("💾 앱 코드 보기 / Copy the full app code"):
    st.code(open(__file__, "r").read(), language="python")

st.markdown("---")
st.subheader("🧩 Requirements 파일 (requirements.txt)")
st.code("streamlit\nfolium\nstreamlit-folium", language="text")
