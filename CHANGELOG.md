# Changelog

All notable changes to the B2B KAM Dashboard project will be documented in this file.

## [Unreleased]
### Added
- 프로젝트 초기 기획안 (`대시보드_화면_기획안.md`) 작성 완료.
- Global Rule에 따른 프로젝트 관리 표준 문서(`PRD.md`, `MEMORY.md`, `CHANGELOG.md`, `README.md`) 세팅.
- 데이터 전처리 및 집계 모듈(`data.py`) 구현.
  - KA/GA 분류 및 `Sum(SLIN_TOTAL)` 기반 집계, 담당 및 상품별 집계 로직 적용.
- Flask 기반 백엔드 라우팅 및 렌더링 서버(`app.py`) 구축.
- 프론트엔드 UI 템플릿(`templates/index.html`) 및 스타일시트(`static/css/style.css`) 구현.
  - 상단 필터 영역 (조회 월, 담당) 추가.
  - 6가지 시각화 차트 추가 (Plotly.js 활용).

### Changed
- UI 및 차트의 용어를 "본부"에서 "담당"으로 전면 수정.
- 대시보드 테마에 Glassmorphism 및 다크 테마 적용, 전역 폰트를 Pretendard로 변경.
- **[MAJOR OVERHAUL]** 기존 다크 테마 기반 구조를 **모던 SaaS Light Theme(화이트/라이트그레이 배경)**로 전면 개편.
- **[UI/UX]** 담당-Tier 크로스분석 및 히트맵에 그라데이션 컬러 매핑(KA: 핑크톤, GA: 그레이톤) 적용.
- **[CLEANUP]** 개발 중 생성된 불필요한 테스트 및 디버깅용 스크립트 파일 일괄 제거.
