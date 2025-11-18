# Base 체인 vs MapleRepair 체인 비교

## 요약
- **Base 체인**: RAG(테이블 요약 검색) → 프롬프트 → LLM → SQL 생성 → 실행. 단일 패스.
- **MapleRepair 체인**: Base 체인으로 1차 SQL 생성 후, 검증·수리 루프 수행.
  - 규칙 기반 오류 감지/수정 → 실패 시 LLM 보조 수리 → `EXPLAIN` 재검증 → 최대 N 라운드 반복.
- **평가 지표**: EX(Execution Accuracy). 각 질문의 정답 라벨과 DB 실행 결과가 일치하면 1로 집계.

## 체인 구조
- **Base** (`chains/text_to_sql_chain.py`)
  - 입력: `question`
  - 단계:
    - 관련 테이블 검색(`DVDRentalRetriever`) → 컨텍스트 포맷 → `ChatPromptTemplate` → `ChatOpenAI` → 문자열 파싱 → SQL 정리
  - 장점: 단순/빠름. 단점: 스키마 환각·문법 오류 시 실패율 상승.

- **MapleRepair** (`v_mungyu/maple_repair_chain.py`)
  - 입력: `question`
  - 단계:
    - Base 체인으로 초기 SQL 생성
    - 검증: `EXPLAIN <sql>` 실행해 오류 수집
    - 규칙 기반 수리(`v_mungyu/repair_utils.py`)
      - 없는 테이블/컬럼 감지(regex) → 실제 스키마에서 근접 후보로 자동 치환
    - LLM 보조 수리
      - 스키마 텍스트와 오류 메시지를 함께 넣고 “수정된 SQL만” 반환하도록 프롬프트 구성
    - 재검증 및 최대 3라운드 반복
  - 목표: 단순 오류는 규칙으로 빠르게 해결하고, 의미적 오류만 LLM에 위임해 비용/지연 최소화.

## 평가 방법(공통)
- **테스트셋**: `experiments/dvdrental_testset.csv` (90개)
- **EX 정의**:
  - 숫자값: 절대 오차 < 0.01
  - 문자열: 소문자/트림 후 완전 일치
- **DB**: `dvdrental` (PostgreSQL + pgvector). Streamlit `web` 컨테이너에서는 `db:5432` 접속.

## 실행 방법
- 테스트셋 생성(한 번만):
```bash
docker exec -it text2sql-web python /app/testset.py
```

- CLI 비교 실행:
```bash
docker exec -it text2sql-web python -u /app/experiments/compare_maple_vs_base.py
```
출력:
- `BASE_ACC=xx.xx% MAPLE_ACC=yy.yy%`
- CSV: `experiments/evaluation/compare_maple_vs_base_<timestamp>.csv`

- Streamlit UI에서 실행:
  - http://localhost:8501 → 탭 "실험결과 1" → 섹션 "Base vs MapleRepair 비교" → [비교 실행]
  - 상단에 `Base EX`, `MapleRepair EX` 메트릭과 하단 상세 테이블 표시

## 결과 해석 가이드
- Base 대비 MapleRepair의 **EX 상승**이 크면 규칙/검증 루프가 오류를 효과적으로 제거한 것.
- `*_error`가 없는 상태에서 `*_match=False`면 의미적 오류(질문 해석/집계 정의)가 원인일 가능성 높음.
- `maple_sql`이 `base_sql` 대비 스키마명·컬럼명 교정, JOIN 축소/정리, CAST/집계 함수 보정 등으로 바뀌는지 확인.

## 비용/지연
- MapleRepair는 라운드 수만큼 LLM 호출이 늘 수 있으나, 규칙 기반 단계에서 많은 케이스가 조기 해결됨.
- 실험 중 속도가 느리면 테스트셋 일부 샘플로 먼저 확인 후 전체 실행 권장.

## 한계와 개선 아이디어
- 규칙 기반 감지는 현재 "없는 테이블/컬럼" 중심. 향후
  - 잘못된 집계/그룹화 패턴, 불필요 JOIN, 스칼라 서브쿼리 → JOIN 변환 등 규칙 확장
- 쿼리 의도 확인용 자연어 피드백 루프 추가(의미 오류 완화)
- 실패 케이스 자동 분석 리포트 생성(오류 유형/빈도)

## 재현성 체크리스트
- `.env`에 `OPENAI_API_KEY` 설정
- Docker: `docker compose up -d --build`
- 초기 임베딩: 컨테이너 시작 시 자동 실행(`init/init_table_docs.py`)
- 테스트셋 CSV 존재 여부 확인
- 비교 실행 후 CSV가 `experiments/evaluation`에 저장되는지 확인
