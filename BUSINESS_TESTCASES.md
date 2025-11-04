# 📊 실무 중심 Text2SQL 테스트 케이스

> DVD 렌탈 비즈니스 실무에서 실제로 물어볼 법한 질문들을 카테고리별로 정리
> 
> **데이터베이스**: PostgreSQL (dvdrental)
> **테이블**: actor, film, film_actor, category, film_category, customer, rental, payment, inventory, store, staff, address, city, country, language

---

## 📈 1. 매출 및 수익 분석 (Revenue & Sales Analysis)

### 기본 매출 지표
```
Q: 전체 총 매출은 얼마인가요?
SQL: SELECT ROUND(SUM(amount), 2) FROM payment;

Q: 고객의 평균 결제 금액은 얼마인가요?
SQL: SELECT ROUND(AVG(amount), 2) FROM payment;

Q: 일별 평균 매출액은?
SQL: SELECT ROUND(AVG(daily_revenue), 2) FROM (SELECT DATE(payment_date) as date, SUM(amount) as daily_revenue FROM payment GROUP BY DATE(payment_date)) sub;

Q: 매출 상위 10% 고객들이 전체 매출에서 차지하는 비율은?
SQL: WITH customer_revenue AS (SELECT customer_id, SUM(amount) as total FROM payment GROUP BY customer_id ORDER BY total DESC), top_10_percent AS (SELECT * FROM customer_revenue LIMIT (SELECT CAST(COUNT(*) * 0.1 AS INT) FROM customer_revenue)) SELECT ROUND(SUM(total) * 100.0 / (SELECT SUM(amount) FROM payment), 2) as contribution_pct FROM top_10_percent;

Q: 결제 금액이 가장 높은 거래 TOP 5는?
SQL: SELECT payment_id, customer_id, amount, payment_date FROM payment ORDER BY amount DESC LIMIT 5;
```

### 카테고리별 매출
```
Q: 어떤 장르가 가장 많은 매출을 올렸나요?
SQL: SELECT c.name, ROUND(SUM(p.amount), 2) as revenue FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY c.name ORDER BY revenue DESC LIMIT 1;

Q: 매출이 가장 낮은 카테고리 3개는?
SQL: SELECT c.name, ROUND(SUM(p.amount), 2) as revenue FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY c.name ORDER BY revenue ASC LIMIT 3;

Q: 카테고리별 평균 거래 금액은?
SQL: SELECT c.name, ROUND(AVG(p.amount), 2) as avg_transaction FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY c.name ORDER BY avg_transaction DESC;
```

---

## 👥 2. 고객 분석 (Customer Analytics)

### 고객 세그먼테이션
```
Q: VIP 고객(총 결제액 상위 5%) 명단을 보여주세요
SQL: SELECT c.customer_id, c.first_name || ' ' || c.last_name as name, ROUND(SUM(p.amount), 2) as total_spent FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spent DESC LIMIT (SELECT CAST(COUNT(DISTINCT customer_id) * 0.05 AS INT) FROM payment);

Q: 한 번만 대여하고 이탈한 고객은 몇 명인가요?
SQL: SELECT COUNT(*) FROM customer c WHERE (SELECT COUNT(*) FROM rental r WHERE r.customer_id = c.customer_id) = 1;

Q: 대여 횟수가 가장 많은 고객의 이름은?
SQL: SELECT first_name || ' ' || last_name as name FROM customer ORDER BY (SELECT COUNT(*) FROM rental r WHERE r.customer_id = customer.customer_id) DESC LIMIT 1;

Q: 고객 1인당 평균 생애 가치(LTV)는?
SQL: SELECT ROUND(AVG(customer_ltv), 2) FROM (SELECT customer_id, SUM(amount) as customer_ltv FROM payment GROUP BY customer_id) sub;

#고객 생애 가치(LTV)는 고객이 특정 제품이나 서비스를 사용하는 시간 동안 창출하는 평균 수익의 추정치입니다.


Q: 가장 많이 대여한 고객의 총 대여 횟수는?
SQL: SELECT COUNT(*) FROM rental r WHERE r.customer_id = (SELECT customer_id FROM rental GROUP BY customer_id ORDER BY COUNT(*) DESC LIMIT 1);
```

### 고객 행동 분석
```
Q: 고객들이 가장 선호하는 영화 장르는?
SQL: SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY c.name ORDER BY COUNT(r.rental_id) DESC LIMIT 1;

Q: 평균적으로 고객들은 몇 일 만에 영화를 반납하나요?
SQL: SELECT ROUND(AVG(EXTRACT(EPOCH FROM (return_date - rental_date))/86400), 2) as avg_days FROM rental WHERE return_date IS NOT NULL;

Q: 주말과 평일 중 언제 대여가 더 많이 일어나나요?
SQL: SELECT CASE WHEN EXTRACT(DOW FROM rental_date) IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END as day_type, COUNT(*) as rental_count FROM rental GROUP BY day_type ORDER BY rental_count DESC;

Q: 활성 고객(active=1)은 몇 명인가요?
SQL: SELECT COUNT(*) FROM customer WHERE active = 1;
```

---

## 📦 3. 재고 및 운영 관리 (Inventory & Operations)

### 재고 최적화
```
Q: 재고가 부족한 인기 영화는 무엇인가요?
SQL: SELECT f.title, COUNT(DISTINCT i.inventory_id) as stock_count, COUNT(r.rental_id) as rental_count FROM film f JOIN inventory i ON f.film_id = i.film_id LEFT JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id, f.title HAVING COUNT(r.rental_id) > 20 AND COUNT(DISTINCT i.inventory_id) < 3 ORDER BY rental_count DESC;

Q: 재고 회전율이 가장 높은 영화 10개는?
SQL: SELECT f.title, COUNT(r.rental_id) as rental_count, COUNT(DISTINCT i.inventory_id) as stock, ROUND(COUNT(r.rental_id)::numeric / NULLIF(COUNT(DISTINCT i.inventory_id), 0), 2) as turnover_rate FROM film f JOIN inventory i ON f.film_id = i.film_id LEFT JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id, f.title ORDER BY turnover_rate DESC LIMIT 10;

Q: 대여가 한 번도 이루어지지 않은 영화는 몇 편인가요?
SQL: SELECT COUNT(*) FROM film f WHERE NOT EXISTS (SELECT 1 FROM inventory i JOIN rental r ON i.inventory_id = r.inventory_id WHERE i.film_id = f.film_id);

Q: 각 스토어별 재고 현황은?
SQL: SELECT s.store_id, COUNT(DISTINCT i.film_id) as unique_films, COUNT(i.inventory_id) as total_inventory FROM store s JOIN inventory i ON s.store_id = i.store_id GROUP BY s.store_id;

Q: 스토어는 몇 개 있나요?
SQL: SELECT COUNT(*) FROM store;
```

### 운영 효율성
```
Q: 반납되지 않은 대여 건수는 몇 건인가요?
SQL: SELECT COUNT(*) FROM rental WHERE return_date IS NULL;

Q: 스태프별 처리한 결제 건수는?
SQL: SELECT s.first_name || ' ' || s.last_name as staff_name, COUNT(p.payment_id) as payment_count, ROUND(SUM(p.amount), 2) as total_amount FROM staff s JOIN payment p ON s.staff_id = p.staff_id GROUP BY s.staff_id, s.first_name, s.last_name;

Q: 스태프는 몇 명인가요?
SQL: SELECT COUNT(*) FROM staff;

Q: 결제가 가장 많이 일어난 시간대는?
SQL: SELECT EXTRACT(HOUR FROM payment_date)::int AS hour_of_day, COUNT(*) AS payment_count FROM payment GROUP BY hour_of_day ORDER BY payment_count DESC LIMIT 1;

Q: 평균 대여 처리 시간은?
SQL: SELECT ROUND(AVG(EXTRACT(EPOCH FROM (return_date - rental_date))/3600), 2) as avg_hours FROM rental WHERE return_date IS NOT NULL;
```

---

## 🎬 4. 콘텐츠 성과 분석 (Content Performance)

### 영화 인기도
```
Q: 가장 많이 대여된 영화의 제목은?
SQL: SELECT f.title FROM film f JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.title ORDER BY COUNT(r.rental_id) DESC LIMIT 1;

Q: 가장 많이 대여된 카테고리는?
SQL: SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON f.film_id = fc.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY c.name ORDER BY COUNT(r.rental_id) DESC LIMIT 1;

Q: 평점별 평균 대여 횟수는?
SQL: SELECT f.rating, ROUND(AVG(rental_count), 2) as avg_rentals FROM (SELECT f.film_id, f.rating, COUNT(r.rental_id) as rental_count FROM film f LEFT JOIN inventory i ON f.film_id = i.film_id LEFT JOIN rental r ON i.inventory_id = r.inventory_id GROUP BY f.film_id, f.rating) sub GROUP BY rating ORDER BY avg_rentals DESC;

Q: 평균 대여료가 가장 높은 카테고리는?
SQL: SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON f.film_id = fc.film_id GROUP BY c.name ORDER BY AVG(f.rental_rate) DESC LIMIT 1;

Q: 평균 길이가 가장 짧은 카테고리는?
SQL: SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON f.film_id = fc.film_id GROUP BY c.name ORDER BY AVG(f.length) ASC LIMIT 1;
```

### 배우 및 출연진
```
Q: 배우는 총 몇 명인가요?
SQL: SELECT COUNT(*) FROM actor;

Q: 가장 많은 배우가 출연한 영화의 제목은?
SQL: SELECT f.title FROM film f JOIN film_actor fa ON f.film_id = fa.film_id GROUP BY f.title ORDER BY COUNT(fa.actor_id) DESC LIMIT 1;

Q: 출연 영화가 10편 이상인 배우는 몇 명인가요?
SQL: SELECT COUNT(*) FROM actor a WHERE (SELECT COUNT(*) FROM film_actor fa WHERE fa.actor_id = a.actor_id) >= 10;

Q: 'Action' 카테고리 영화들의 평균 길이는 얼마인가요?
SQL: SELECT ROUND(AVG(f.length), 2) FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON c.category_id = fc.category_id WHERE c.name = 'Action';
```

---

## 🌍 5. 지역별 분석 (Geographic Analysis)

### 지역 성과
```
Q: 국가는 몇 개 있나요?
SQL: SELECT COUNT(*) FROM country;

Q: 도시는 몇 개 있나요?
SQL: SELECT COUNT(*) FROM city;

Q: 가장 많은 고객이 있는 도시는?
SQL: SELECT ci.city FROM city ci JOIN address a ON ci.city_id = a.city_id JOIN customer c ON a.address_id = c.address_id GROUP BY ci.city ORDER BY COUNT(c.customer_id) DESC LIMIT 1;

Q: 국가별 고객 수를 내림차순으로 상위 5개 국가는?
SQL: SELECT co.country, COUNT(c.customer_id) as customer_count FROM country co JOIN city ci ON co.country_id = ci.country_id JOIN address a ON ci.city_id = a.city_id JOIN customer c ON a.address_id = c.address_id GROUP BY co.country ORDER BY customer_count DESC LIMIT 5;

Q: 매출이 가장 높은 도시 TOP 10은?
SQL: SELECT ci.city, co.country, ROUND(SUM(p.amount), 2) as revenue FROM city ci JOIN country co ON ci.country_id = co.country_id JOIN address a ON ci.city_id = a.city_id JOIN customer c ON a.address_id = c.address_id JOIN payment p ON c.customer_id = p.customer_id GROUP BY ci.city, co.country ORDER BY revenue DESC LIMIT 10;
```

---

## 📊 6. 트렌드 및 예측 (Trends & Forecasting)

### 시계열 분석
```
Q: 요일별 평균 대여 횟수는?
SQL: SELECT EXTRACT(DOW FROM rental_date) as day_of_week, COUNT(*) as rental_count FROM rental GROUP BY day_of_week ORDER BY day_of_week;

Q: 시간대별 대여 횟수는?
SQL: SELECT EXTRACT(HOUR FROM rental_date) as hour, COUNT(*) as rental_count FROM rental GROUP BY hour ORDER BY hour;

Q: 월별 대여 트렌드는?
SQL: SELECT EXTRACT(YEAR FROM rental_date) as year, EXTRACT(MONTH FROM rental_date) as month, COUNT(*) as rental_count FROM rental GROUP BY year, month ORDER BY year, month;
```

### 성장 지표
```
Q: 월간 활성 고객(MAU) 수는?
SQL: SELECT EXTRACT(YEAR FROM rental_date) as year, EXTRACT(MONTH FROM rental_date) as month, COUNT(DISTINCT customer_id) as active_users FROM rental GROUP BY year, month ORDER BY year, month;

Q: 고객 재방문율(Retention Rate)은?
SQL: WITH first_rental AS (SELECT customer_id, MIN(DATE(rental_date)) as first_date FROM rental GROUP BY customer_id), repeat_customers AS (SELECT fr.customer_id FROM first_rental fr JOIN rental r ON fr.customer_id = r.customer_id WHERE DATE(r.rental_date) > fr.first_date GROUP BY fr.customer_id) SELECT ROUND(COUNT(DISTINCT rc.customer_id) * 100.0 / COUNT(DISTINCT fr.customer_id), 2) as retention_rate FROM first_rental fr LEFT JOIN repeat_customers rc ON fr.customer_id = rc.customer_id;

Q: 대여 횟수가 5회 이상인 고객은 몇 명인가요?
SQL: SELECT COUNT(*) FROM (SELECT customer_id FROM rental GROUP BY customer_id HAVING COUNT(*) >= 5) sub;
```

---

## 💰 7. 가격 전략 (Pricing Strategy)

### 가격 최적화
```
Q: 대여료 구간별 매출 분포는?
SQL: SELECT CASE WHEN rental_rate < 1 THEN 'Budget (<$1)' WHEN rental_rate < 3 THEN 'Standard ($1-$3)' ELSE 'Premium ($3+)' END as price_tier, COUNT(DISTINCT f.film_id) as film_count, ROUND(SUM(p.amount), 2) as total_revenue FROM film f JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY price_tier ORDER BY total_revenue DESC;

Q: 영화의 평균 대여료는 얼마인가요?
SQL: SELECT ROUND(AVG(rental_rate), 2) FROM film;

Q: 영화의 최대 대여료는 얼마인가요?
SQL: SELECT MAX(rental_rate) FROM film;

Q: 영화의 최소 대여료는 얼마인가요?
SQL: SELECT MIN(rental_rate) FROM film;

Q: 평균보다 비싼 영화는 몇 편인가요?
SQL: SELECT COUNT(*) FROM film WHERE rental_rate > (SELECT AVG(rental_rate) FROM film);

Q: 대여료이 4.99달러인 영화는 몇 편인가요?
SQL: SELECT COUNT(*) FROM film WHERE rental_rate = 4.99;
```

---

## 🎯 8. 마케팅 및 프로모션 (Marketing & Promotion)

### 캠페인 효과
```
Q: 'Comedy' 카테고리 영화는 몇 편인가요?
SQL: SELECT COUNT(*) FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON c.category_id = fc.category_id WHERE c.name = 'Comedy';

Q: 영화가 가장 많은 카테고리는?
SQL: SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY COUNT(fc.film_id) DESC LIMIT 1;

Q: 언어는 몇 개 등록되어 있나요?
SQL: SELECT COUNT(*) FROM language;

Q: 추천 시스템용: 'Action' 영화를 좋아하는 고객들이 함께 본 다른 장르는?
SQL: SELECT c2.name as recommended_category, COUNT(*) as co_rental_count FROM rental r1 JOIN inventory i1 ON r1.inventory_id = i1.inventory_id JOIN film f1 ON i1.film_id = f1.film_id JOIN film_category fc1 ON f1.film_id = fc1.film_id JOIN category c1 ON fc1.category_id = c1.category_id JOIN rental r2 ON r1.customer_id = r2.customer_id JOIN inventory i2 ON r2.inventory_id = i2.inventory_id JOIN film f2 ON i2.film_id = f2.film_id JOIN film_category fc2 ON f2.film_id = fc2.film_id JOIN category c2 ON fc2.category_id = c2.category_id WHERE c1.name = 'Action' AND c2.name != 'Action' GROUP BY c2.name ORDER BY co_rental_count DESC LIMIT 5;
```

---

## 🔍 9. 이상 탐지 및 리스크 관리 (Anomaly Detection & Risk)

### 이상 거래 탐지
```
Q: 비정상적으로 높은 금액의 결제 건은?
SQL: SELECT payment_id, customer_id, amount, payment_date FROM payment WHERE amount > (SELECT AVG(amount) + 3 * STDDEV(amount) FROM payment) ORDER BY amount DESC;

Q: 같은 날 10회 이상 대여한 고객은?
SQL: SELECT customer_id, DATE(rental_date) as date, COUNT(*) as rental_count FROM rental GROUP BY customer_id, DATE(rental_date) HAVING COUNT(*) >= 10;

Q: 연체율이 높은 고객 TOP 20은?
SQL: SELECT c.customer_id, c.first_name || ' ' || c.last_name as name, COUNT(r.rental_id) as total_rentals, COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) as overdue_count, ROUND(COUNT(CASE WHEN r.return_date IS NULL THEN 1 END) * 100.0 / NULLIF(COUNT(r.rental_id), 0), 2) as overdue_rate FROM customer c JOIN rental r ON c.customer_id = r.customer_id GROUP BY c.customer_id, c.first_name, c.last_name HAVING COUNT(r.rental_id) >= 5 ORDER BY overdue_rate DESC LIMIT 20;

Q: 연체 중인 대여 건수는?
SQL: SELECT COUNT(*) FROM rental WHERE return_date IS NULL;
```

---

## 📋 10. 경영진 대시보드 (Executive Dashboard)

### 핵심 KPI
```
Q: 전체 대여 건수는?
SQL: SELECT COUNT(*) FROM rental;

Q: 전체 고객 수는?
SQL: SELECT COUNT(*) FROM customer;

Q: 전체 영화 수는?
SQL: SELECT COUNT(*) FROM film;

Q: 평균보다 긴 영화는 몇 편인가요?
SQL: SELECT COUNT(*) FROM film WHERE length > (SELECT AVG(length) FROM film);

Q: 얼마나 결제를 해야 전체 유저 중에서 상위 10%에 해당할까?
SQL: SELECT percentile_disc(0.9) WITHIN GROUP (ORDER BY total_amount) AS top_10_percent_threshold FROM (SELECT customer_id, SUM(amount) AS total_amount FROM payment GROUP BY customer_id) AS customer_totals;
```

---

## 🎓 사용 가이드

### 테스트 방법
1. **난이도별 분류**: 각 카테고리 내에서 쿼리 복잡도 증가
2. **비즈니스 맥락**: 실제 의사결정에 필요한 질문
3. **확장 가능**: 다른 도메인(이커머스, SaaS 등)에 적용 가능

### 평가 기준
- ✅ **정확성**: 올바른 SQL 생성 및 실행
- ✅ **완전성**: 모든 필요한 조인과 필터 포함
- ✅ **효율성**: 최적화된 쿼리 구조
- ✅ **비즈니스 이해도**: 질문 의도 파악

### 추가 테스트 시나리오
- 모호한 질문 처리
- 동의어 및 유사 표현 이해
- 복합 조건 처리
- 시간대 및 날짜 형식 변환

---

## 📊 테스트셋 통계

### 카테고리별 질문 수
1. **매출 및 수익 분석**: 10개 질문
2. **고객 분석**: 10개 질문
3. **재고 및 운영 관리**: 11개 질문
4. **콘텐츠 성과 분석**: 9개 질문
5. **지역별 분석**: 6개 질문
6. **트렌드 및 예측**: 7개 질문
7. **가격 전략**: 6개 질문
8. **마케팅 및 프로모션**: 4개 질문
9. **이상 탐지 및 리스크**: 4개 질문
10. **경영진 대시보드**: 5개 질문

**총 72개의 실무 중심 질문**

### 난이도 분포
- **초급** (단일 테이블, 기본 집계): ~30%
- **중급** (2-3개 테이블 조인, GROUP BY): ~50%
- **고급** (서브쿼리, 윈도우 함수, 복잡한 조인): ~20%

### 주요 SQL 패턴
- COUNT, SUM, AVG, MIN, MAX 집계 함수
- JOIN (INNER, LEFT) 다중 테이블 조인
- GROUP BY, HAVING 그룹화 및 필터링
- 서브쿼리 (상관, 비상관)
- 윈도우 함수 (percentile_disc)
- CASE WHEN 조건부 로직
- EXTRACT 날짜/시간 함수

---

## 🚀 다음 단계

1. **Python 스크립트로 변환**: testset.py 형식으로 변환하여 자동 테스트
2. **정답 레이블 추가**: 각 쿼리의 예상 결과값 추가
3. **실행 및 검증**: 실제 데이터베이스에서 쿼리 실행 및 결과 검증
4. **난이도 태깅**: 각 질문에 난이도 레벨 추가
5. **오류 분석**: Text2SQL 모델의 오류 패턴 분석
