# utils/llm_client.py
import os
import logging
from typing import Dict, Any
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

from utils.logger import get_logger

# .env 파일 로드
load_dotenv()

logger = get_logger("LLMClient")

class LLMClient:
    """OpenAI 기반 LLM 호출 래퍼 클래스"""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 .env에 설정되지 않았습니다.")

        try:
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            logger.exception("OpenAI 클라이언트 초기화 실패")
            raise e

    def chat(self, prompt: str, max_tokens: int = 3000) -> str:
        """GPT 챗 완료 호출"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            return content if content else ""

        except OpenAIError as e:
            logger.error("OpenAI API 오류 발생")
            raise e

        except Exception as e:
            logger.exception("LLM 호출 실패")
            raise e
