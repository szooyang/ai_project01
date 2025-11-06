# main.py
import streamlit as s

st.set_page_config(page_title="MBTI 기반 진로 추천", page_icon="🎯", layout="centered")

st.title("🎓 MBTI로 보는 진로 추천")
st.markdown("MBTI 16가지 중 하나를 골라주면, 그 유형에 잘 맞는 진로 2가지를 추천해줄게! ✨\n\n친근한 말투로 설명해줄게 — 부담없이 골라봐~")

MBTI_LIST = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

# 진로 데이터: 각 MBTI에 대해 2개 직업, 추천 학과, 성격 설명
CAREER_DB = {
    "ISTJ": [
        {"job":"공무원 / 행정직", "majors":"행정학, 법학, 경영학", "personality":"책임감이 강하고 꼼꼼함. 규칙과 절차를 잘 따르는 타입이에요. ✅"},
        {"job":"회계사 / 재무직", "majors":"회계학, 경영학, 세무학", "personality":"디테일을 챙기고 숫자 관리에 강함. 신뢰받는 실무형!"}
    ],
    "ISFJ": [
        {"job":"간호사 / 보건의료", "majors":"간호학, 보건학, 사회복지학", "personality":"친절하고 섬세함. 사람 돌보는 걸 좋아해요. 💊"},
        {"job":"초등교사 / 교육직", "majors":"교육학, 아동학, 특수교육", "personality":"책임감 있고 인내심 많음. 학생들과 안정적으로 잘 지내요."}
    ],
    "INFJ": [
        {"job":"임상심리사 / 상담사", "majors":"심리학, 상담학, 사회복지학", "personality":"사람의 마음을 깊이 이해하려는 공감형. 의미있는 일을 좋아함. 💬"},
        {"job":"컨텐츠 기획 / 작가", "majors":"문예창작, 디자인학, 미디어학", "personality":"창의적이고 통찰력 있음. 메시지 전달을 잘해요."}
    ],
    "INTJ": [
        {"job":"연구원 / 데이터 과학자", "majors":"수학, 통계학, 컴퓨터공학", "personality":"전략적이고 논리적. 복잡한 문제 풀기를 즐김. 🧠"},
        {"job":"기획자 / 전략컨설턴트", "majors":"경영학, 산업공학, 경제학", "personality":"장기 플랜 세우기 좋아하고 목표 지향적."}
    ],
    "ISTP": [
        {"job":"기계공학자 / 엔지니어", "majors":"기계공학, 전자공학, 재료공학", "personality":"손으로 만지고 해결하는 실전형. 즉흥적 문제해결 능력 굿. ⚙️"},
        {"job":"IT개발자 (프론트/백엔드)", "majors":"컴퓨터공학, 소프트웨어학", "personality":"실용적이고 기술적 사고가 빠름. 도구 다루는 것에 능함."}
    ],
    "ISFP": [
        {"job":"디자이너 / 시각예술가", "majors":"시각디자인, 산업디자인, 예술학", "personality":"감각적이고 미적인 것에 민감. 자기 표현을 좋아함. 🎨"},
        {"job":"작곡가 / 음향 엔지니어", "majors":"음악학, 사운드엔지니어링", "personality":"감성적이고 세심함. 소리에 민감하고 창작을 즐김."}
    ],
    "INFP": [
        {"job":"문학가 / 시나리오 작가", "majors":"문예창작, 국문학, 영상학", "personality":"이상주의자, 깊은 자기표현과 가치 추구. ✍️"},
        {"job":"NGO/사회복지 활동가", "majors":"사회복지학, 국제관계학", "personality":"가치 중심으로 행동함. 약자와 이슈에 공감 많음."}
    ],
    "INTP": [
        {"job":"연구개발자 / 이론물리학자", "majors":"물리학, 수학, 컴퓨터학", "personality":"호기심이 많고 개념적 사고에 강함. 이론 다루기를 즐김. 🔬"},
        {"job":"소프트웨어 아키텍트", "majors":"컴퓨터공학, 소프트웨어학", "personality":"논리적 설계와 구조화에 탁월함."}
    ],
    "ESTP": [
        {"job":"영업 / 마케팅 실무자", "majors":"경영학, 광고홍보학", "personality":"적응력 빠르고 사람 만나는 걸 좋아함. 행동력 최고! 💼"},
        {"job":"응급의료 / 소방관", "majors":"응급구조학, 소방안전학", "personality":"실전에서 빠른 판단과 행동을 잘함."}
    ],
    "ESFP": [
        {"job":"연예/엔터테인먼트 (MC, 배우)", "majors":"연기학, 방송연예학, 공연예술", "personality":"사교적이고 무대 적응력 좋음. 에너지 넘침. 🎤"},
        {"job":"관광/서비스업 (호텔리어)", "majors":"관광학, 호텔경영학", "personality":"사람 서비스하고 즐겁게 일하는 타입."}
    ],
    "ENFP": [
        {"job":"마케팅 콘텐츠 크리에이터", "majors":"미디어학, 커뮤니케이션학", "personality":"창의적이고 아이디어 샘솟음. 사람과 아이디어를 잇는 역할. 🌟"},
        {"job":"창업가 / 스타트업", "majors":"경영학, 창업학, 디자인씽킹", "personality":"모험심 있고 비전을 의욕적으로 추구함."}
    ],
    "ENTP": [
        {"job":"컨설턴트 / 기획자", "majors":"경영학, 경제학, 산업공학", "personality":"논쟁적이고 아이디어 뱅크. 문제 재구성에 능함. 💡"},
        {"job":"벤처 창업가 / 제품 매니저", "majors":"컴퓨터공학, 경영학, 디자인", "personality":"빠른 실험과 피벗을 즐기며, 설득력 있음."}
    ],
    "ESTJ": [
        {"job":"기업 관리직 / 운영매니저", "majors":"경영학, 산업경영학", "personality":"조직 관리 능력 뛰어나고 책임감 강함. 시스템 좋아함. 🏢"},
        {"job":"법조계 (판사/검사/변호사)", "majors":"법학, 정치학", "personality":"규칙과 질서를 중시하며 논리적 판단을 잘함."}
    ],
    "ESFJ": [
        {"job":"간호·보건 행정", "majors":"보건행정, 간호학, 사회복지학", "personality":"사교적이고 타인 돌보는 걸 즐김. 팀워크가 장점. 🤝"},
        {"job":"교육행정 / 인사(HR)", "majors":"교육학, 경영학(인사)", "personality":"사람 관리와 조화를 중시하는 조직형."}
    ],
    "ENFJ": [
        {"job":"인사·교육 담당자 (HRD)", "majors":"교육학, 인사관리, 심리학", "personality":"사람을 이끌고 성장시키는 리더형. 공감 능력 탁월. 🌱"},
        {"job":"PR / 커뮤니케이션 전문가", "majors":"커뮤니케이션학, 홍보학", "personality":"메시지 전달과 사람 연결에 강함."}
    ],
    "ENTJ": [
        {"job":"경영자 / 임원", "majors":"경영학, MBA, 경제학", "personality":"목표 지향적이고 리더십 강함. 전략 세우는 걸 좋아함. 🚀"},
        {"job":"전략 컨설턴트", "majors":"경영학, 경제학, 산업공학", "personality":"분석적이고 큰 그림을 설계하는 능력 우수."}
    ],
}

st.sidebar.header("설정")
st.sidebar.write("앱 버전: 1.0 • 라이브러리: streamlit만 사용")

col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://static.streamlit.io/examples/dice.jpg", caption="진로 찾기 🎲", use_column_width=True)
with col2:
    st.write("사용법: 왼쪽에서 MBTI를 골라주세요. 그러면 그 유형에 어울리는 **진로 2가지**와 각 진로에 맞는 **학과**와 **성격 팁**을 알려줄게요. 😄")

mbti_choice = st.selectbox("👉 당신의 MBTI를 골라줘", MBTI_LIST)

st.markdown("---")

# 보여주기
st.subheader(f"✨ {mbti_choice}에게 어울리는 진로")
careers = CAREER_DB.get(mbti_choice)

if careers:
    for i, c in enumerate(careers, start=1):
        st.markdown(f"### {i}. {c['job']}  { '⭐' * (3-i+1) }")
        st.markdown(f"- **추천 학과**: {c['majors']}")
        st.markdown(f"- **어떤 성격이 잘 맞을까?**: {c['personality']}")
        # 친근한 추가 팁
        if i == 1:
            st.info("팁: 1번 진로가 좀 더 안정적이고 전통적인 경로야. 준비는 꾸준히 하는 걸 추천해! 📚")
        else:
            st.success("팁: 2번 진로는 좀 더 창의적이거나 실무 중심일 확률이 높아. 실무경험을 쌓아봐! 🔍")

st.markdown("---")
st.write("원하면 친구 MBTI로도 여러 번 확인해봐~ 여러 사람 비교하면 진로 아이디어가 더 잘 보일거야. 😎")
st.caption("※ 이 추천은 참고용이에요. 진로는 다양한 경험과 자기 탐색을 통해 결정하세요!")

# 하단에 간단한 복사 버튼 (Streamlit 자체 기능 이용)
st.write("")
if st.button("결과 텍스트 복사하기"):
    result_lines = [f"{mbti_choice} 추천 진로:"]
    for c in careers:
        result_lines.append(f"- {c['job']} | 학과: {c['majors']} | 성격: {c['personality']}")
    st.write("\n".join(result_lines))
    st.balloons()
