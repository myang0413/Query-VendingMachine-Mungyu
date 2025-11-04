# 📚 Text2SQL 표준 평가 방법론

## 🎓 학계 표준 평가 지표

### 1. **Exact Match (EM)** ⭐⭐⭐
**출처**: Spider (Yu et al., 2018), WikiSQL

```python
# 정의
EM = (생성된 SQL == 정답 SQL) ? 1 : 0

# 특징
- 가장 엄격한 평가
- 공백, 대소문자 정규화 후 비교
- 문제점: 의미적으로 동일해도 표현이 다르면 0점
```

**예시:**
```sql
# 정답
SELECT COUNT(*) FROM customer;

# 생성 (EM = 0, 하지만 의미는 동일)
SELECT count(*) from customer;
```

---

### 2. **Execution Accuracy (EX)** ⭐⭐⭐⭐⭐
**출처**: Spider, BIRD, WikiSQL

```python
# 정의
EX = (생성 SQL 실행 결과 == 정답 SQL 실행 결과) ? 1 : 0

# 특징
- 실무에서 가장 중요
- SQL 표현은 달라도 결과가 같으면 정답
- 실제 사용 가능성 평가
```

**예시:**
```sql
# 정답
SELECT COUNT(*) FROM customer WHERE active = 1;

# 생성 (EX = 1, 결과 동일)
SELECT COUNT(customer_id) FROM customer WHERE active = 1;
```

---

### 3. **Component Matching** ⭐⭐⭐⭐
**출처**: Spider (Yu et al., 2018)

SQL을 구성 요소별로 분해하여 평가:

| 구성 요소 | 설명 | 가중치 |
|----------|------|--------|
| **SELECT** | 선택 컬럼 | 20% |
| **FROM** | 테이블 선택 | 20% |
| **WHERE** | 필터 조건 | 20% |
| **GROUP BY** | 그룹화 | 15% |
| **ORDER BY** | 정렬 | 10% |
| **Keywords** | JOIN, DISTINCT 등 | 15% |

```python
# F1 Score 계산
Precision = |생성 ∩ 정답| / |생성|
Recall = |생성 ∩ 정답| / |정답|
F1 = 2 * Precision * Recall / (Precision + Recall)
```

---

### 4. **Test-Suite Accuracy** ⭐⭐⭐
**출처**: Zhong et al., 2020

여러 데이터베이스 상태에서 테스트:

```python
# 정의
TSA = Σ(생성 SQL 결과 == 정답 SQL 결과) / 테스트 케이스 수

# 특징
- 다양한 데이터 상태에서 검증
- 엣지 케이스 처리 능력 평가
- 더 robust한 평가
```

---

### 5. **Partial Credit (부분 점수)** ⭐⭐⭐⭐
**출처**: BIRD (Li et al., 2023)

완전히 틀려도 부분적으로 맞으면 점수 부여:

| 평가 항목 | 배점 |
|----------|------|
| 올바른 테이블 선택 | 15% |
| 올바른 컬럼 선택 | 15% |
| JOIN 정확성 | 20% |
| WHERE 조건 정확성 | 20% |
| 집계 함수 사용 | 15% |
| GROUP BY 정확성 | 10% |
| ORDER BY 정확성 | 5% |

---

## 📊 주요 벤치마크 데이터셋

### 1. **Spider** (2018) 🏆
- **규모**: 200개 DB, 10,181개 질문
- **특징**: 크로스 도메인, 복잡한 쿼리
- **난이도**: Easy (28%), Medium (40%), Hard (24%), Extra Hard (8%)
- **평가**: EM, EX, Component Matching

```python
# Spider 난이도 분류 기준
Easy: 단일 테이블, 기본 SELECT
Medium: 1-2개 JOIN, 집계 함수
Hard: 2-3개 JOIN, 서브쿼리
Extra Hard: 3개 이상 JOIN, 중첩 쿼리
```

### 2. **WikiSQL** (2017)
- **규모**: 26,521개 테이블, 80,654개 질문
- **특징**: 단순한 쿼리, 단일 테이블
- **평가**: Logical Form Accuracy, EX

### 3. **BIRD** (2023) 🆕
- **규모**: 95개 실무 DB, 12,751개 질문
- **특징**: 실무 중심, 더러운 데이터
- **평가**: EX, Valid Efficiency Score (VES)

```python
# BIRD의 VES (Valid Efficiency Score)
VES = (정확도) × (1 - 실행시간 페널티)
```

### 4. **CoSQL** (2019)
- **규모**: 3,007개 대화, 15,598개 질문
- **특징**: 대화형 Text2SQL
- **평가**: Question Match, Interaction Match

---

## 🔬 우리 프로젝트와 표준 방법 비교

| 평가 지표 | 표준 방법 | 우리 구현 | 상태 |
|----------|----------|----------|------|
| **Exact Match** | ✅ Spider, WikiSQL | ✅ 구현 완료 | ✅ |
| **Execution Accuracy** | ✅ 모든 벤치마크 | ✅ 구현 완료 | ✅ |
| **Valid SQL** | ✅ BIRD | ✅ 구현 완료 | ✅ |
| **Component Matching** | ✅ Spider | ✅ 추가 구현 | ✅ |
| **Partial Credit** | ✅ BIRD | ✅ 추가 구현 | ✅ |
| **Test-Suite Accuracy** | ✅ Zhong et al. | ✅ 추가 구현 | ✅ |
| **난이도 분류** | ✅ Spider | ✅ 구현 완료 | ✅ |
| **카테고리별 분석** | ✅ BIRD | ✅ 구현 완료 | ✅ |
| **오류 분석** | ✅ BIRD | ✅ 추가 구현 | ✅ |

---

## 📈 추가로 고려할 평가 방법

### 1. **Human Evaluation** (인간 평가)
```python
# 평가 기준
- 자연스러운 SQL인가?
- 최적화되어 있는가?
- 가독성이 좋은가?

# 방법
- 전문가 3명이 독립적으로 평가
- Cohen's Kappa로 일치도 측정
```

### 2. **Robustness Test** (강건성 테스트)
```python
# 테스트 케이스
1. 오타가 있는 질문
2. 모호한 질문
3. 복잡한 자연어 표현
4. 도메인 특화 용어

# 예시
"고객들이 가장 좋아하는 영화는?" (모호함)
"렌탈이 제일 많이 된 무비는?" (오타)
```

### 3. **Efficiency Score** (효율성 점수)
```python
# BIRD의 VES
VES = Accuracy × (1 - Latency_Penalty)

# 실행 시간 페널티
if execution_time > threshold:
    penalty = (execution_time - threshold) / threshold
else:
    penalty = 0
```

### 4. **Cross-Database Generalization**
```python
# 평가 방법
1. DB A에서 학습
2. DB B에서 테스트
3. 일반화 능력 측정

# 지표
Generalization Score = Accuracy_on_unseen_DB / Accuracy_on_seen_DB
```

---

## 🎯 업계 표준 성능 벤치마크

### Spider 리더보드 (2024년 기준)

| 순위 | 모델 | EM | EX | 연도 |
|------|------|----|----|------|
| 1 | GPT-4 + CoT | 85.3% | 91.2% | 2023 |
| 2 | DAIL-SQL | 83.1% | 89.6% | 2023 |
| 3 | DIN-SQL | 74.2% | 85.3% | 2023 |
| 4 | T5-3B | 71.5% | 82.4% | 2022 |
| 5 | PICARD | 69.8% | 79.3% | 2021 |

### BIRD 리더보드

| 순위 | 모델 | EX | VES | 연도 |
|------|------|----|----|------|
| 1 | GPT-4 Turbo | 54.89% | 52.84% | 2024 |
| 2 | Claude 3 Opus | 50.17% | 48.32% | 2024 |
| 3 | GPT-4 | 46.35% | 44.69% | 2023 |

**참고**: BIRD는 실무 데이터라 난이도가 훨씬 높음

---

## 📝 평가 리포트 작성 가이드

### 표준 리포트 포맷

```markdown
# Text2SQL 모델 평가 리포트

## 1. 실험 설정
- 모델: GPT-3.5-turbo
- 데이터셋: dvdrental (52 test cases)
- 날짜: 2025-11-04

## 2. 전체 성능
| 지표 | 점수 | 표준 (Spider) |
|------|------|---------------|
| Exact Match | 67.3% | 70%+ |
| Execution Accuracy | 86.5% | 85%+ |
| Valid SQL | 92.3% | 90%+ |

## 3. 난이도별 성능
| 난이도 | 케이스 수 | EX | 표준 |
|--------|----------|-------|------|
| Easy | 20 | 95.0% | 90%+ |
| Medium | 28 | 85.0% | 80%+ |
| Hard | 4 | 50.0% | 60%+ |

## 4. 오류 분석
- Syntax Error: 5건 (9.6%)
- Wrong Table: 3건 (5.8%)
- Join Error: 2건 (3.8%)

## 5. 개선 방향
1. 고급 난이도 성능 향상 필요
2. JOIN 조건 생성 개선
3. 서브쿼리 처리 강화
```

---

## 🔄 지속적 평가 프로세스

### 1주차: 베이스라인
```python
# 기본 프롬프트로 평가
baseline_results = evaluate(model, testset, prompt="basic")
save_results(baseline_results, "baseline_week1.json")
```

### 2주차: 프롬프트 개선
```python
# 개선된 프롬프트로 평가
improved_results = evaluate(model, testset, prompt="improved")

# 비교
improvement = compare(improved_results, baseline_results)
print(f"개선율: {improvement:.2%}")
```

### 3주차: 모델 변경
```python
# GPT-4로 업그레이드
gpt4_results = evaluate("gpt-4", testset, prompt="improved")

# 비용 대비 성능 분석
cost_benefit = analyze_cost_benefit(gpt4_results, improved_results)
```

---

## 📚 참고 논문

### 필수 논문
1. **Spider**: Yu et al., "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task", EMNLP 2018
2. **WikiSQL**: Zhong et al., "Seq2SQL: Generating Structured Queries from Natural Language using Reinforcement Learning", 2017
3. **BIRD**: Li et al., "Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs", NeurIPS 2023

### 고급 논문
4. **Test-Suite Accuracy**: Zhong et al., "Semantic Evaluation for Text-to-SQL with Distilled Test Suites", EMNLP 2020
5. **DAIL-SQL**: Gao et al., "Text-to-SQL Empowered by Large Language Models: A Benchmark Evaluation", 2023
6. **DIN-SQL**: Pourreza & Rafiei, "DIN-SQL: Decomposed In-Context Learning of Text-to-SQL with Self-Correction", 2023

---

## ✅ 체크리스트: 표준 평가 준수

- [ ] Exact Match 구현
- [ ] Execution Accuracy 구현
- [ ] Valid SQL 검증
- [ ] Component Matching 구현
- [ ] Partial Credit 구현
- [ ] 난이도별 분류
- [ ] 카테고리별 분석
- [ ] 오류 분석 및 분류
- [ ] 실행 시간 측정
- [ ] 리포트 자동 생성
- [ ] 결과 시각화
- [ ] 벤치마크와 비교

---

## 🎉 결론

**우리 프로젝트는 학계 표준 평가 방법을 충실히 따르고 있으며, 추가로 고급 평가 지표까지 구현했습니다!**

### 우리의 강점
✅ Spider, BIRD 등 주요 벤치마크의 평가 방법 모두 구현
✅ Component Matching, Partial Credit 등 고급 지표 포함
✅ 실무 중심 테스트 케이스 (비즈니스 질문)
✅ 자동화된 평가 및 리포트 생성

### 추가 개선 가능
🔧 Human Evaluation 추가
🔧 Cross-Database 테스트
🔧 Robustness Test 강화
🔧 더 많은 테스트 케이스 (현재 52개 → 200개+)
