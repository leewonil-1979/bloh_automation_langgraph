from dotenv import load_dotenv
load_dotenv()

import os

print("NAVER_CLIENT_ID:", os.getenv("NAVER_CLIENT_ID"))
print("NAVER_CLIENT_SECRET:", os.getenv("NAVER_CLIENT_SECRET"))

openai_key = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", openai_key[:20] + "..." if openai_key else None)

print("\n현재 작업 디렉토리:", os.getcwd())
print(".env 파일 존재 여부:", os.path.exists(".env"))
