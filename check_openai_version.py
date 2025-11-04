"""OpenAI 패키지 버전 및 API 테스트"""
import openai
print(f"OpenAI 버전: {openai.__version__}")

# API 테스트
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 임베딩 테스트
try:
    print("\n테스트 1: input=문자열")
    response = client.embeddings.create(
        input="테스트",
        model="text-embedding-3-small"
    )
    print("✅ 성공!")
except Exception as e:
    print(f"❌ 실패: {e}")

try:
    print("\n테스트 2: input=[문자열]")
    response = client.embeddings.create(
        input=["테스트"],
        model="text-embedding-3-small"
    )
    print("✅ 성공!")
except Exception as e:
    print(f"❌ 실패: {e}")
