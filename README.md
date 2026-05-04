# B2B KAM Dashboard v2

## Overview
B2B Key Account Management(KAM) 대시보드는 전사, 담당, 담당자 단위의 영업 실적을 다각도로 분석하고, 타겟팅할 미도입 영역(Whitespace)을 도출하여 세일즈 액션 플랜을 수립하도록 돕는 웹 기반 인텔리전스 애플리케이션입니다.

## Key Features
1. **필터링 시스템**: 상단 컨트롤 패널에서 특정 월(YYYYMM) 및 담당(조직)을 선택하여 맞춤형 데이터 조회.
2. **전사 종합 실적**: 최고 경영진을 위한 전사 매출(Hero KPI), KA vs GA 비중, 및 Tier별 수익 구조 조망.
3. **조직 성과 분석**: 담당별 KA/GA 비중 점검 및 담당-Tier별 크로스 분석.
4. **상품 믹스 업셀링**: 실무 영업 담당자를 위한 담당별 상품 히트맵, Tier별 상품 믹스(히트맵) 제공 및 미도입 상품 타겟팅 보조.
5. **인사이트 발굴**: 영업 담당자(Rep)별 생산성 분석 스캐터 플롯 제공.

## Technology Stack
- **Backend**: Python 3, Flask 1.1.2
- **Data Processing**: Pandas 1.1.3
- **Visualization**: Plotly 4.10.0 (Python & JS)
- **Frontend**: HTML5, CSS3 (Glassmorphism Dark Theme, Pretendard Font)

## Data Source
- `synthetic_b2b_dashboard_20k.csv` 데이터 기반으로 구동됩니다.

## Installation & Usage

1. **필수 패키지 설치**
   해당 프로젝트 폴더에서 아래 명령어로 의존성을 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

2. **서버 실행**
   Flask 애플리케이션을 구동합니다.
   ```bash
   python app.py
   ```

3. **대시보드 접속**
   웹 브라우저를 열고 `http://127.0.0.1:5001` 주소로 접속합니다.
