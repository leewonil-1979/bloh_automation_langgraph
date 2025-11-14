# utils/llm_client.py
import os
import logging
from typing import Dict, Any, Literal
from openai import OpenAI, OpenAIError
from anthropic import Anthropic, AnthropicError
from anthropic.types import TextBlock
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


class ClaudeClient:
    """Claude (Anthropic) 기반 LLM 호출 래퍼 클래스"""

    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.")

        try:
            self.client = Anthropic(api_key=api_key)
        except Exception as e:
            logger.exception("Anthropic 클라이언트 초기화 실패")
            raise e

    def chat(self, prompt: str, max_tokens: int = 3000) -> str:
        """Claude 챗 완료 호출"""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Claude 3 Haiku (저렴하고 빠름)
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Claude API 응답 형식: response.content[0].text
            if response.content and len(response.content) > 0:
                content_block = response.content[0]
                # isinstance로 TextBlock 확인
                if isinstance(content_block, TextBlock):
                    return content_block.text
            return ""

        except AnthropicError as e:
            logger.error(f"Anthropic API 오류 발생: {e}")
            raise e

        except Exception as e:
            logger.exception("Claude 호출 실패")
            raise e


class HybridLLMClient:
    """
    하이브리드 LLM 클라이언트
    - 작업 유형에 따라 GPT 또는 Claude를 자동 선택
    - 비용 효율성과 성능의 균형 유지
    """

    def __init__(self) -> None:
        # GPT 초기화 (필수)
        try:
            self.gpt_client = LLMClient()
        except Exception as e:
            logger.error("GPT 클라이언트 초기화 실패")
            raise e

        # Claude 초기화 (선택)
        try:
            self.claude_client = ClaudeClient()
            self.claude_available = True
            logger.info("✅ Claude API 사용 가능")
        except Exception as e:
            logger.warning(f"⚠️ Claude API 사용 불가 (GPT만 사용): {e}")
            self.claude_available = False

    def chat(
        self, 
        prompt: str, 
        max_tokens: int = 3000,
        prefer_model: Literal["gpt", "claude", "auto"] = "auto",
        task_type: Literal["simple", "creative", "analytical"] = "simple"
    ) -> str:
        """
        프롬프트에 따라 최적의 모델 선택
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 토큰 수
            prefer_model: 선호 모델 ("gpt", "claude", "auto")
            task_type: 작업 유형
                - simple: 단순 작업 (GPT 사용)
                - creative: 창의적 작업 (Claude 우선)
                - analytical: 분석 작업 (Claude 우선)
        
        Returns:
            LLM 응답 텍스트
        """
        
        # 명시적으로 GPT 요청
        if prefer_model == "gpt":
            logger.info("🤖 GPT-4o-mini 사용")
            return self.gpt_client.chat(prompt, max_tokens)
        
        # 명시적으로 Claude 요청
        if prefer_model == "claude":
            if self.claude_available:
                logger.info("🧠 Claude 3.5 Sonnet 사용")
                return self.claude_client.chat(prompt, max_tokens)
            else:
                logger.warning("⚠️ Claude 불가, GPT로 대체")
                return self.gpt_client.chat(prompt, max_tokens)
        
        # auto: 작업 유형에 따라 자동 선택
        if task_type == "simple":
            logger.info("🤖 GPT-4o-mini 사용 (단순 작업)")
            return self.gpt_client.chat(prompt, max_tokens)
        
        # creative, analytical 작업은 Claude 우선
        if self.claude_available:
            logger.info(f"🧠 Claude 3.5 Sonnet 사용 ({task_type} 작업)")
            return self.claude_client.chat(prompt, max_tokens)
        else:
            logger.warning(f"⚠️ Claude 불가, GPT로 대체 ({task_type} 작업)")
            return self.gpt_client.chat(prompt, max_tokens)

