# 실무 중심 Text2SQL 테스트셋 생성 코드
import pandas as pd

data = [
    # 1. 매출 및 수익 분석
    ["전체 총 매출은 얼마인가요?", "SELECT ROUND(SUM(amount), 2) FROM payment;", "revenue_analysis", "초급"],
    ["고객의 평균 결제 금액은 얼마인가요?", "SELECT ROUND(AVG(amount), 2) FROM payment;", "revenue_analysis", "초급"],
    ["일별 평균 매출액은?", "SELECT ROUND(AVG(daily_revenue), 2) FROM (SELECT DATE(payment_date) as date, SUM(amount) as daily_revenue FROM payment GROUP BY DATE(payment_date)) sub;", "revenue_analysis", "중급"],
    ["매출 상위 10% 고객들이 전체 매출에서 차지하는 비율은?", "WITH customer_revenue AS (SELECT customer_id, SUM(amount) as total FROM payment GROUP BY customer_id ORDER BY total DESC), top_10_percent AS (SELECT * FROM customer_revenue LIMIT (SELECT CAST(COUNT(*) * 0.1 AS INT) FROM customer_revenue)) SELECT ROUND(SUM(total) * 100.0 / (SELECT SUM(amount) FROM payment), 2) as contribution_pct FROM top_10_percent;", "revenue_analysis", "고급"],
    ["결제 금액이 가장 높은 거래 TOP 5는?", "SELECT payment_id, customer_id, amount, payment_date FROM payment ORDER BY amount DESC LIMIT 5;", "revenue_analysis", "초급"],
    ["어떤 장르가 가장 많은 매출을 올렸나요?", "SELECT c.name, ROUND(SUM(p.amount), 2) as revenue FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY c.name ORDER BY revenue DESC LIMIT 1;", "revenue_analysis", "중급"],
    ["매출이 가장 낮은 카테고리 3개는?", "SELECT c.name, ROUND(SUM(p.amount), 2) as revenue FROM category c JOIN film_category fc ON c.category_id = fc.category_id JOIN film f ON fc.film_id = f.film_id JOIN inventory i ON f.film_id = i.film_id JOIN rental r ON i.inventory_id = r.inventory_id JOIN payment p ON r.rental_id = p.rental_id GROUP BY c.name ORDER BY revenue ASC LIMIT 3;", "revenue_analysis", "중급"],
    
    # 2. 고객 분석
    ["VIP 고객(총 결제액 상위 5%) 명단을 보여주세요", "SELECT c.customer_id, c.first_name || ' ' || c.last_name as name, ROUND(SUM(p.amount), 2) as total_spent FROM customer c JOIN payment p ON c.customer_id = p.customer_id GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spent DESC LIMIT (SELECT CAST(COUNT(DISTINCT customer_id) * 0.05 AS INT) FROM payment);", "customer_analysis", "중급"],
    ["한 번만 대여하고 이탈한 고객은 몇 명인가요?", "SELECT COUNT(*) FROM customer c WHERE (SELECT COUNT(*) FROM rental r WHERE r.customer_id = c.customer_id) = 1;", "customer_analysis", "중급"],
    ["이메일 주소에 'gmail'이 포함된 고객은 몇 명인가요?", "SELECT COUNT(*) FROM customer WHERE email LIKE '%gmail%';", "customer_analysis", "초급"],
    ["고객 1인당 평균 생애 가치(LTV)는?", "SELECT ROUND(AVG(customer_ltv), 2) FROM (SELECT customer_id, SUM(amount) as customer_ltv FROM payment GROUP BY customer_id) sub;", "customer_analysis", "중급"],
    ["대여 이력이 없는 고객은 몇 명인가요?", "SELECT COUNT(*) FROM customer c WHERE NOT EXISTS (SELECT 1 FROM rental r WHERE r.customer_id = c.customer_id);", "customer_analysis", "중급"],
    ["주말(토,일)에 대여한 고객 수는?", "SELECT COUNT(DISTINCT customer_id) FROM rental WHERE EXTRACT(DOW FROM rental_date) IN (0, 6);", "customer_analysis", "중급"],
    ["평균적으로 고객들은 몇 일 만에 영화를 반납하나요?", "SELECT ROUND(AVG(EXTRACT(EPOCH FROM (return_date - rental_date))/86400), 2) as avg_days FROM rental WHERE return_date IS NOT NULL;", "customer_analysis", "중급"],
    ["활성 고객(active=1)은 몇 명인가요?", "SELECT COUNT(*) FROM customer WHERE active = 1;", "customer_analysis", "초급"],
    
    # 3. 재고 및 운영 관리
    ["재고가 5개 미만인 영화는 몇 편인가요?", "SELECT COUNT(DISTINCT f.film_id) FROM film f JOIN inventory i ON f.film_id = i.film_id GROUP BY f.film_id HAVING COUNT(i.inventory_id) < 5;", "inventory_operations", "중급"],
    ["각 스토어별 재고 현황은?", "SELECT s.store_id, COUNT(DISTINCT i.film_id) as unique_films, COUNT(i.inventory_id) as total_inventory FROM store s JOIN inventory i ON s.store_id = i.store_id GROUP BY s.store_id;", "inventory_operations", "중급"],
    ["전체 재고(inventory) 수는?", "SELECT COUNT(*) FROM inventory;", "inventory_operations", "초급"],
    ["반납되지 않은 대여 건수는 몇 건인가요?", "SELECT COUNT(*) FROM rental WHERE return_date IS NULL;", "inventory_operations", "초급"],
    ["스태프별 처리한 결제 건수는?", "SELECT s.first_name || ' ' || s.last_name as staff_name, COUNT(p.payment_id) as payment_count, ROUND(SUM(p.amount), 2) as total_amount FROM staff s JOIN payment p ON s.staff_id = p.staff_id GROUP BY s.staff_id, s.first_name, s.last_name;", "inventory_operations", "중급"],
    ["주소(address) 테이블에 등록된 주소는 몇 개인가요?", "SELECT COUNT(*) FROM address;", "inventory_operations", "초급"],
    ["오늘 발생한 결제 건수는?", "SELECT COUNT(*) FROM payment WHERE DATE(payment_date) = CURRENT_DATE;", "inventory_operations", "초급"],
    
    # 4. 콘텐츠 성과 분석
    ["대여 기간(rental_duration)이 7일 이상인 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE rental_duration >= 7;", "content_performance", "초급"],
    ["'R' 등급 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE rating = 'R';", "content_performance", "초급"],
    ["카테고리는 총 몇 개인가요?", "SELECT COUNT(*) FROM category;", "content_performance", "초급"],
    ["영화 제목에 'LOVE'가 포함된 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE title LIKE '%LOVE%';", "content_performance", "초급"],
    ["출연 영화가 가장 많은 배우의 이름은?", "SELECT a.first_name || ' ' || a.last_name as actor_name FROM actor a JOIN film_actor fa ON a.actor_id = fa.actor_id GROUP BY a.actor_id, a.first_name, a.last_name ORDER BY COUNT(fa.film_id) DESC LIMIT 1;", "content_performance", "중급"],
    ["'Horror' 카테고리에 속한 영화의 평균 대여료는?", "SELECT ROUND(AVG(f.rental_rate), 2) FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON c.category_id = fc.category_id WHERE c.name = 'Horror';", "content_performance", "중급"],
    ["출연 영화가 10편 이상인 배우는 몇 명인가요?", "SELECT COUNT(*) FROM actor a WHERE (SELECT COUNT(*) FROM film_actor fa WHERE fa.actor_id = a.actor_id) >= 10;", "content_performance", "중급"],
    ["영화 길이가 120분 이상인 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE length >= 120;", "content_performance", "초급"],
    
    # 5. 지역별 분석
    ["'United States'에 있는 도시는 몇 개인가요?", "SELECT COUNT(*) FROM city ci JOIN country co ON ci.country_id = co.country_id WHERE co.country = 'United States';", "geographic_analysis", "중급"],
    ["고객이 없는 도시는 몇 개인가요?", "SELECT COUNT(*) FROM city ci WHERE NOT EXISTS (SELECT 1 FROM address a JOIN customer c ON a.address_id = c.address_id WHERE a.city_id = ci.city_id);", "geographic_analysis", "중급"],
    ["가장 많은 고객이 있는 도시는?", "SELECT ci.city FROM city ci JOIN address a ON ci.city_id = a.city_id JOIN customer c ON a.address_id = c.address_id GROUP BY ci.city ORDER BY COUNT(c.customer_id) DESC LIMIT 1;", "geographic_analysis", "중급"],
    ["국가별 고객 수를 내림차순으로 상위 5개 국가는?", "SELECT co.country, COUNT(c.customer_id) as customer_count FROM country co JOIN city ci ON co.country_id = ci.country_id JOIN address a ON ci.city_id = a.city_id JOIN customer c ON a.address_id = c.address_id GROUP BY co.country ORDER BY customer_count DESC LIMIT 5;", "geographic_analysis", "중급"],
    
    # 6. 트렌드 및 예측
    ["요일별 평균 대여 횟수는?", "SELECT EXTRACT(DOW FROM rental_date) as day_of_week, COUNT(*) as rental_count FROM rental GROUP BY day_of_week ORDER BY day_of_week;", "trends_forecasting", "중급"],
    ["시간대별 대여 횟수는?", "SELECT EXTRACT(HOUR FROM rental_date) as hour, COUNT(*) as rental_count FROM rental GROUP BY hour ORDER BY hour;", "trends_forecasting", "중급"],
    ["대여 횟수가 5회 이상인 고객은 몇 명인가요?", "SELECT COUNT(*) FROM (SELECT customer_id FROM rental GROUP BY customer_id HAVING COUNT(*) >= 5) sub;", "trends_forecasting", "중급"],
    
    # 7. 가격 전략
    ["대여료가 0.99달러인 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE rental_rate = 0.99;", "pricing_strategy", "초급"],
    ["대여료가 2.99달러 이상인 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE rental_rate >= 2.99;", "pricing_strategy", "초급"],
    ["교체 비용(replacement_cost)이 20달러 이상인 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE replacement_cost >= 20;", "pricing_strategy", "초급"],
    ["평균보다 비싼 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE rental_rate > (SELECT AVG(rental_rate) FROM film);", "pricing_strategy", "중급"],
    
    # 8. 마케팅 및 프로모션
    ["'Drama' 카테고리 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film f JOIN film_category fc ON f.film_id = fc.film_id JOIN category c ON c.category_id = fc.category_id WHERE c.name = 'Drama';", "marketing_promotion", "중급"],
    ["영화가 가장 적은 카테고리는?", "SELECT c.name FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY COUNT(fc.film_id) ASC LIMIT 1;", "marketing_promotion", "중급"],
    ["특수 기능(special_features)에 'Deleted Scenes'가 포함된 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE 'Deleted Scenes' = ANY(special_features);", "marketing_promotion", "중급"],
    
    # 9. 이상 탐지 및 리스크
    ["같은 날 10회 이상 대여한 고객은?", "SELECT customer_id, DATE(rental_date) as date, COUNT(*) as rental_count FROM rental GROUP BY customer_id, DATE(rental_date) HAVING COUNT(*) >= 10;", "anomaly_detection", "중급"],
    ["연체 중인 대여 건수는?", "SELECT COUNT(*) FROM rental WHERE return_date IS NULL;", "anomaly_detection", "초급"],
    
    # 10. 경영진 대시보드
    ["전체 결제 건수는?", "SELECT COUNT(*) FROM payment;", "executive_dashboard", "초급"],
    ["대여 기록이 있는 고객은 몇 명인가요?", "SELECT COUNT(DISTINCT customer_id) FROM rental;", "executive_dashboard", "초급"],
    ["재고가 있는 영화는 몇 편인가요?", "SELECT COUNT(DISTINCT film_id) FROM inventory;", "executive_dashboard", "초급"],
    ["평균보다 긴 영화는 몇 편인가요?", "SELECT COUNT(*) FROM film WHERE length > (SELECT AVG(length) FROM film);", "executive_dashboard", "중급"],
    ["얼마나 결제를 해야 전체 유저 중에서 상위 10%에 해당할까?", "SELECT percentile_disc(0.9) WITHIN GROUP (ORDER BY total_amount) AS top_10_percent_threshold FROM (SELECT customer_id, SUM(amount) AS total_amount FROM payment GROUP BY customer_id) AS customer_totals;", "executive_dashboard", "고급"],
]

if __name__ == "__main__":
    df = pd.DataFrame(data, columns=["question", "sql", "category", "difficulty"])
    
    # CSV 저장
    csv_path = "experiments/business_testset.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    print(f"✅ 비즈니스 테스트셋 생성 완료: {csv_path}")
    print(f"📊 총 {len(df)}개의 테스트 케이스")
    print("\n카테고리별 분포:")
    print(df['category'].value_counts())
    print("\n난이도별 분포:")
    print(df['difficulty'].value_counts())
