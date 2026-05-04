# Product Requirements Document (PRD): B2B KAM Dashboard

## 1. Project Overview
**What**: `synthetic_b2b_dashboard_20k.csv` 데이터를 기반으로 전사, 담당(조직), 상품 믹스 관점의 성과를 모니터링하고 타겟팅 영업 기회를 발굴하기 위한 B2B Key Account Management (KAM) 대시보드.
**Why**: 최고 경영진의 전사 건강도 파악, 본부장/팀장의 담당(조직) 성과 모니터링, 그리고 실무 영업 담당자의 미도입 영역(Whitespace) 발굴 및 실질적인 세일즈 액션 플랜 수립을 위함.

## 2. Core Requirements
### 2.1. 데이터 전제 조건
- **집계 함수**: 모든 차트 및 지표 합산은 `Sum(SLIN_TOTAL)` 기준 연산 (중복 합산 방지).
- **Tier 분류 체계**: 
  - Key Account (KA): Tier 1, Tier 2, Tier 3
  - General Account (GA): W.seg, 핵심, 일반

### 2.2. 필수 구현 뷰 (Views)
1. **필터 컨트롤 패널**: 상단에 조회 월, 고객 유형(KA/GA), Tier, 담당(Division), 팀(Team)을 선택하는 다중 필터 구성.
2. **전사 종합 실적 뷰**: 총매출 요약(카드), KA vs GA 매출 비중(도넛), KA/GA 산하 Tier별 실적(묶은 세로 막대).
3. **조직 단위 성과 및 드릴다운 뷰 (동적 뷰 적용)**: 
   - '담당' 필터 선택 시 하위 차트(KA/GA 비중 스택 차트, 크로스 분석 차트, 상품 믹스 히트맵)가 **'팀' 단위로 자동 전환**되어 세밀한 분석 제공.
4. **상품 믹스 기반 업셀링 발굴 뷰**: 담당x상품 크로스 히트맵, Tier별 상품 믹스 (히트맵).
5. **인사이트 발굴 뷰**: 영업 담당자 생산성 스캐터 플롯. (향후 MoM 성장률 추적 워터폴, KA Top 10 리더보드 추가 가능)

## 3. Future Enhancements (Gap Analysis)
- 목표 대비 달성률 (Target vs Actual) 도입
- 신규 획득 vs 이탈 고객 추적 (New Logos vs Churn)
- 영업 파이프라인/수주 가망 금액 연동 (Pipeline / Funnel)
