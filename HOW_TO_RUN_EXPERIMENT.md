# 🚀 실험 실행 가이드

## 📋 실험 순서

### ✅ 1단계: 테스트셋 생성

```bash
# business_testset.py 실행
python business_testset.py
```

**출력 예시:**
```
✅ 비즈니스 테스트셋 생성 완료: experiments/business_testset.csv
📊 총 52개의 테스트 케이스

카테고리별 분포:
customer_analysis        8
content_performance      8
inventory_operations     7
revenue_analysis         7
...
```

**생성 파일:** `experiments/business_testset.csv`

---

### ✅ 2단계: 평가 실행 (3가지 방법)

#### 방법 A: 명령줄에서 직접 실행 (권장)

```bash
# 전체 평가 실행
python evaluate_llm.py
```

#### 방법 B: Streamlit 웹 인터페이스 사용

```bash
# Streamlit 앱 실행
streamlit run main.py
```

그 다음:
1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 사이드바에서 "실험 결과" 탭 클릭
3. "실험 시작" 버튼 클릭
4. 실시간으로 결과 확인

#### 방법 C: 제한된 평가 (빠른 테스트)

`evaluate_llm.py` 파일 수정:
```python
# 10개만 평가 (테스트용)
results_df = evaluator.evaluate_all(limit=10)
```

---

### ✅ 3단계: 결과 확인

평가 완료 후 `experiments/evaluation/` 폴더에 생성:

#### 📄 1. 상세 결과 CSV
```
experiments/evaluation/results_20251104_182000.csv
```

#### 📄 2. 리포트 JSON
```
experiments/evaluation/report_20251104_182000.json
```

#### 📺 3. 콘솔 출력
```
================================================================================
📊 Text2SQL LLM 성능 평가 리포트
================================================================================

📅 평가 시간: 2025-11-04T18:20:00
📝 총 테스트 케이스: 52개

🎯 전체 성능 지표:
  • Exact Match (EM):         35개 (67.31%)
  • Execution Accuracy (EX):  45개 (86.54%)
  • Valid SQL (VS):           48개 (92.31%)
  • 평균 생성 시간:           1.23초
```

---

## 🔧 환경 설정 확인

### 필수 확인사항

```bash
# 1. Docker 컨테이너 실행 확인
docker ps

# 출력에 text2sql-db가 있어야 함
CONTAINER ID   IMAGE         PORTS                    NAMES
abc123def456   postgres:15   0.0.0.0:5432->5432/tcp   text2sql-db

# 2. 데이터베이스 연결 테스트
docker exec -it text2sql-db psql -U user -d dvdrental -c "SELECT COUNT(*) FROM customer;"

# 3. OpenAI API 키 확인
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows CMD
$env:OPENAI_API_KEY    # Windows PowerShell
```

---

## 📊 실험 시나리오

### 시나리오 1: 기본 성능 평가

```bash
# 1. 테스트셋 생성
python business_testset.py

# 2. 평가 실행
python evaluate_llm.py

# 3. 결과 확인
cat experiments/evaluation/report_*.json
```

### 시나리오 2: 프롬프트 A/B 테스트

```python
# evaluate_llm.py 수정

# 프롬프트 버전 A
chain_v1 = Text2SQLChain(prompt_version="v1")
evaluator_v1 = Text2SQLEvaluator(testset_path, db_url, chain=chain_v1)
results_v1 = evaluator_v1.evaluate_all()

# 프롬프트 버전 B
chain_v2 = Text2SQLChain(prompt_version="v2")
evaluator_v2 = Text2SQLEvaluator(testset_path, db_url, chain=chain_v2)
results_v2 = evaluator_v2.evaluate_all()

# 비교
compare_results(results_v1, results_v2)
```

### 시나리오 3: 모델 비교 (GPT-4 vs GPT-3.5)

```python
# config/llm_config.py에서 모델 변경

# GPT-4 평가
os.environ["MODEL_NAME"] = "gpt-4"
results_gpt4 = evaluator.evaluate_all()

# GPT-3.5 평가
os.environ["MODEL_NAME"] = "gpt-3.5-turbo"
results_gpt35 = evaluator.evaluate_all()

# 비용 대비 성능 분석
```

### 시나리오 4: 난이도별 성능 분석

```python
# 난이도별 필터링
easy_cases = df[df['difficulty'] == '초급']
medium_cases = df[df['difficulty'] == '중급']
hard_cases = df[df['difficulty'] == '고급']

# 각각 평가
easy_results = evaluator.evaluate_subset(easy_cases)
medium_results = evaluator.evaluate_subset(medium_cases)
hard_results = evaluator.evaluate_subset(hard_cases)
```

---

## 📈 결과 분석

### 1. CSV 파일 분석 (Excel/Python)

```python
import pandas as pd

# 결과 로드
df = pd.read_csv('experiments/evaluation/results_20251104_182000.csv')

# 성공/실패 분석
success = df[df['execution_match'] == True]
failed = df[df['execution_match'] == False]

print(f"성공: {len(success)}개 ({len(success)/len(df)*100:.2f}%)")
print(f"실패: {len(failed)}개 ({len(failed)/len(df)*100:.2f}%)")

# 카테고리별 성능
category_performance = df.groupby('category')['execution_match'].mean()
print("\n카테고리별 정확도:")
print(category_performance.sort_values(ascending=False))

# 난이도별 성능
difficulty_performance = df.groupby('difficulty')['execution_match'].mean()
print("\n난이도별 정확도:")
print(difficulty_performance)
```

### 2. 실패 케이스 분석

```python
# 실패한 케이스만 필터링
failed_cases = df[df['execution_match'] == False]

# 오류 타입별 분류
print("\n실패 케이스 분석:")
for idx, row in failed_cases.iterrows():
    print(f"\n질문: {row['question']}")
    print(f"카테고리: {row['category']}")
    print(f"난이도: {row['difficulty']}")
    print(f"생성 SQL: {row['generated_sql'][:100]}...")
    print(f"오류: {row['error'][:100] if row['error'] else 'N/A'}...")
```

### 3. 시각화 (선택)

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 카테고리별 성능 차트
plt.figure(figsize=(12, 6))
category_perf = df.groupby('category')['execution_match'].mean() * 100
category_perf.plot(kind='bar')
plt.title('카테고리별 Execution Accuracy')
plt.ylabel('정확도 (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('experiments/evaluation/category_performance.png')

# 난이도별 성능 차트
plt.figure(figsize=(8, 6))
difficulty_perf = df.groupby('difficulty')['execution_match'].mean() * 100
difficulty_perf.plot(kind='bar', color=['green', 'orange', 'red'])
plt.title('난이도별 Execution Accuracy')
plt.ylabel('정확도 (%)')
plt.tight_layout()
plt.savefig('experiments/evaluation/difficulty_performance.png')
```

---

## 🐛 문제 해결

### Q1: "ModuleNotFoundError: No module named 'chains'"

```bash
# 프로젝트 루트 디렉토리에서 실행하세요
cd C:\Users\user\Desktop\쿼리자판기\Query-VendingMachine_Mungyu
python evaluate_llm.py
```

### Q2: "데이터베이스 연결 오류"

```bash
# Docker 컨테이너 확인
docker ps

# 컨테이너가 없으면 시작
docker-compose up -d

# 컨테이너 재시작
docker restart text2sql-db
```

### Q3: "OpenAI API 오류 (Rate Limit)"

```python
# evaluate_llm.py에서 sleep 시간 증가
time.sleep(1.0)  # 0.5 → 1.0으로 변경

# 또는 limit 사용
results_df = evaluator.evaluate_all(limit=10)
```

### Q4: "파일을 찾을 수 없습니다"

```bash
# experiments 폴더 생성
mkdir experiments
mkdir experiments\evaluation

# 테스트셋 먼저 생성
python business_testset.py
```

---

## 📝 체크리스트

### 실험 전
- [ ] Docker 컨테이너 실행 중
- [ ] OpenAI API 키 설정
- [ ] `experiments/` 폴더 존재
- [ ] 테스트셋 생성 완료 (`business_testset.csv`)

### 실험 중
- [ ] 콘솔에서 진행 상황 확인
- [ ] 오류 발생 시 즉시 중단하지 말고 로그 확인
- [ ] API Rate Limit 주의

### 실험 후
- [ ] 결과 CSV 파일 확인
- [ ] 리포트 JSON 파일 확인
- [ ] 실패 케이스 분석
- [ ] 개선 방향 도출

---

## 🎯 예상 소요 시간

| 단계 | 소요 시간 | 비고 |
|------|----------|------|
| 테스트셋 생성 | 1초 | - |
| 평가 실행 (52개) | 5-10분 | API 속도에 따라 |
| 결과 분석 | 5-10분 | 수동 분석 |
| **총 소요 시간** | **10-20분** | - |

---

## 💡 팁

1. **처음에는 limit=10으로 테스트**
   ```python
   results_df = evaluator.evaluate_all(limit=10)
   ```

2. **실패 케이스 먼저 분석**
   - 패턴을 찾아 프롬프트 개선

3. **카테고리별로 나눠서 평가**
   - 특정 카테고리만 집중 개선

4. **버전 관리**
   - 각 실험마다 결과 파일 백업
   - 프롬프트 버전 기록

---

## 🚀 다음 단계

1. **기본 평가 완료** → 성능 지표 확인
2. **실패 케이스 분석** → 오류 패턴 파악
3. **프롬프트 개선** → A/B 테스트
4. **재평가** → 개선 효과 측정
5. **반복** → 목표 성능 달성까지

---

**🎉 이제 실험을 시작하세요!**

```bash
# 한 번에 실행
python business_testset.py && python evaluate_llm.py
```
