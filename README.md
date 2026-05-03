# 🍎 안테처 (Anteacher): 미적분 기반 금융 교육 플랫폼

**안테처(Anteacher)**는 주식 시장의 흐름을 수학적 관점(미적분)에서 분석하고, AI가 초보 투자자의 눈높이에 맞춰 설명해 주는 스마트 금융 대시보드입니다.

![Anteacher Screenshot](https://raw.githubusercontent.com/your-username/Anteacher/main/screenshot.png) *(배포 후 스크린샷으로 교체하세요)*

## ✨ 주요 기능
- **📐 수학적 추세 분석**: 주가의 1계 도함수(기울기)와 2계 도함수(가속도)를 계산하여 현재 상승 에너지와 흐름의 변화를 시각화합니다.
- **🟡 골든크로스 탐지**: 5일 이동평균선이 20일선을 돌파하는 지점을 실시간으로 포착하여 차트에 표시합니다.
- **🤖 AI 안테처 리포트**: Gemini 1.5 Flash AI가 복잡한 수치를 "초등학생도 이해할 수 있는" 친근한 언어로 요약해 줍니다.
- **📰 뉴스 심리 지수**: 최신 뉴스를 AI가 분석하여 시장의 긍정/부정 분위기를 점수화합니다.
- **🚀 오늘의 추천 종목**: 매일 아침, 상승 에너지가 가장 강한 상위 종목들을 선정하여 대시보드에 띄워줍니다.
- **📢 디스코드 실시간 알림**: 주가 흐름에 유의미한 변화가 감지되면 즉시 디스코드로 알림을 전송합니다.

## 🛠️ 기술 스택
- **Language**: Python 3.9+
- **Frontend**: Streamlit
- **Visualization**: Plotly
- **AI Engine**: Google Gemini (Generative AI)
- **Data Source**: FinanceDataReader, Yahoo Finance, NAVER News RSS

## ⚙️ 설치 및 실행 방법

1. 저장소 복제
```bash
git clone https://github.com/your-username/Anteacher.git
cd Anteacher
```

2. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
`.env` 파일을 생성하고 아래 키를 입력하세요.
```text
GEMINI_API_KEY=your_key
FRED_API_KEY=your_key
NAVER_CLIENT_ID=your_id
NAVER_CLIENT_SECRET=your_secret
NEWS_API_KEY=your_key
DISCORD_WEBHOOK_URL=your_webhook_url
```

4. 실행
```bash
streamlit run app.py
```

## 📜 라이선스
본 프로젝트는 교육용 목적으로 제작되었으며, 분석 결과는 실제 투자 수익을 보장하지 않습니다. 모든 투자의 책임은 본인에게 있습니다.
