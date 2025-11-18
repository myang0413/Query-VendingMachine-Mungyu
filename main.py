import streamlit as st
import pandas as pd
import os
import time

# LangChain 모듈 임포트
from chains.text_to_sql_chain import invoke_text_to_sql_chain
from chains.text_to_sql_chain import create_text_to_sql_chain
from v_mungyu.maple_repair_chain import create_maple_repair_chain
from experiments.experiment_1.run import run as ex1_run
from utils import run_query, log_step


def main():
    st.title("📝 Text2SQL Demo with LangChain")

    tabs = st.tabs(["Text2SQL", "실험결과 1"])

    with tabs[0]:
        natural_query = st.text_input(
            "Enter your question:",
            "List the title and release year of movies.",
        )

        if st.button("Run", key="run_text2sql"):
            try:
                log_step("🎯 사용자 요청 시작")
                sql = invoke_text_to_sql_chain(natural_query)
                log_step("Step 6: SQL 정리 완료", {"정리된_SQL": sql})
                st.code(sql, language="sql")

                try:
                    log_step("Step 7: SQL 쿼리 실행 중...", {"SQL": sql})
                    rows = run_query(query=sql, dvd=True)
                    df = pd.DataFrame(rows)
                    log_step("Step 8: 쿼리 실행 완료", {
                        "반환된_행_수": len(rows),
                        "컬럼_수": len(df.columns),
                        "컬럼명": list(df.columns),
                    })
                    st.dataframe(df)
                    log_step("✅ 전체 파이프라인 완료", {
                        "최종_결과_행수": len(rows),
                        "처리_상태": "성공",
                    })
                    st.session_state["experiment_result"] = df
                except Exception as e:
                    log_step("❌ 쿼리 실행 오류 발생", {
                        "에러_타입": type(e).__name__,
                        "에러_메시지": str(e),
                    })
                    st.error(f"Error running query: {e}")
            except Exception as e:
                log_step("❌ SQL 생성 오류 발생", {
                    "에러_타입": type(e).__name__,
                    "에러_메시지": str(e),
                })
                st.error(f"Error generating SQL: {e}")

    with tabs[1]:
        st.header("실험결과_1")
        st.write(": 기본 스키마 + 테이블 요약 --> RAG 유사 문서 n개 검색 --> 프롬프트 생성 --> SQL 생성 --> 실행")
        csv_path = "experiments/experiment_1/result.csv"

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if "experiment_1" not in st.session_state:
                st.session_state["experiment_1"] = df
            st.dataframe(st.session_state["experiment_1"])
        else:
            st.info("아직 실험 결과가 없습니다.")
            if st.button("실험 실행하기"):
                df = ex1_run()
                st.session_state["experiment_1"] = df
                st.dataframe(st.session_state["experiment_1"])

        st.subheader("Base vs MapleRepair 비교")
        testset_csv = "experiments/dvdrental_testset.csv"
        if not os.path.exists(testset_csv):
            st.warning("테스트셋이 없습니다. 터미널에서 'docker exec text2sql-web python /app/testset.py' 실행 후 다시 시도하세요.")
        else:
            if st.button("비교 실행", key="run_compare"):
                df = pd.read_csv(testset_csv)
                base_chain = create_text_to_sql_chain()
                maple_chain = create_maple_repair_chain()
                records = []
                b_ok = 0
                m_ok = 0
                progress = st.progress(0)
                total = len(df)

                def _scalar(rows):
                    if not rows:
                        return None
                    r = rows[0]
                    if isinstance(r, dict):
                        return list(r.values())[0] if r else None
                    return r[0] if len(r) > 0 else None

                def _match(expected, actual):
                    try:
                        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                            return abs(float(expected) - float(actual)) < 0.01
                        return str(expected).strip().lower() == str(actual).strip().lower()
                    except Exception:
                        return str(expected) == str(actual)

                for idx, row in df.iterrows():
                    q = row["question"]
                    label = row["label"]
                    b_sql = base_chain.invoke(q)
                    try:
                        b_rows = run_query(b_sql, dvd=True)
                        b_val = _scalar(b_rows)
                        b_match = _match(label, b_val)
                    except Exception as e:
                        b_val = None
                        b_match = False
                    if b_match:
                        b_ok += 1

                    m_sql = maple_chain.invoke(q)
                    try:
                        m_rows = run_query(m_sql, dvd=True)
                        m_val = _scalar(m_rows)
                        m_match = _match(label, m_val)
                    except Exception as e:
                        m_val = None
                        m_match = False
                    if m_match:
                        m_ok += 1

                    records.append({
                        "question": q,
                        "expected": label,
                        "base_sql": b_sql,
                        "base_result": b_val,
                        "base_match": b_match,
                        "maple_sql": m_sql,
                        "maple_result": m_val,
                        "maple_match": m_match,
                    })
                    progress.progress(int((idx + 1) / total * 100))
                    time.sleep(0.1)

                base_acc = b_ok / total * 100 if total else 0
                maple_acc = m_ok / total * 100 if total else 0
                st.metric("Base EX", f"{base_acc:.2f}%", None)
                st.metric("MapleRepair EX", f"{maple_acc:.2f}%", None)
                out_df = pd.DataFrame(records)
                st.dataframe(out_df)
                st.session_state["compare_results"] = out_df


if __name__ == "__main__":
    main()