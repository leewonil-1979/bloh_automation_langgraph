"""
Idea Refiner Node
사용자와 대화형 티키타카를 통해 초기 아이디어를 구체화하는 노드
GPT + Claude 하이브리드 전략:
- GPT: 질문 생성, 충분성 판단 (빠르고 저렴)
- Claude: 아이디어 합성, 세부 정보 추출 (창의적이고 고품질)
"""

from typing import Dict, Any, List, Optional
from utils.llm_client import LLMClient, HybridLLMClient
from utils.logger import get_logger

logger = get_logger("IdeaRefinerNode")


class IdeaRefinerNode:
    """사용자와 대화를 통해 아이디어를 정교화하는 노드 (GPT+Claude 하이브리드)"""
    
    def __init__(self):
        self.gpt_client = LLMClient()  # 질문 생성용 (빠름)
        self.hybrid_client = HybridLLMClient()  # 아이디어 합성용 (고품질)
        self.conversation_history = []
        self.max_questions = 5  # 최대 질문 횟수
    
    def refine_interactive(self, initial_idea: str, auto_mode: bool = False) -> Dict[str, Any]:
        """
        대화형 아이디어 정교화
        
        Args:
            initial_idea: 사용자의 초기 아이디어
            auto_mode: True면 자동으로 답변 생성 (테스트용), False면 실제 입력 받음
            
        Returns:
            {
                "initial_idea": str,
                "refined_idea": str,
                "conversation_history": List[Dict],
                "extracted_details": Dict
            }
        """
        logger.info(f"💡 초기 아이디어: {initial_idea}")
        print("\n" + "="*80)
        print("🎯 아이디어 구체화 대화를 시작합니다!")
        print("="*80)
        print(f"\n💭 입력하신 아이디어: '{initial_idea}'\n")
        
        self.conversation_history = []
        current_context = initial_idea
        
        # 1단계: 초기 분석 및 질문 생성
        for question_round in range(1, self.max_questions + 1):
            print(f"\n--- 질문 {question_round}/{self.max_questions} ---")
            
            # AI가 질문 생성
            question = self._generate_question(current_context, question_round)
            print(f"\n🤖 AI: {question}")
            
            # 사용자 응답 받기
            if auto_mode:
                answer = self._generate_auto_answer(question, current_context)
                print(f"👤 (자동 답변): {answer}")
            else:
                answer = input("\n👤 답변: ").strip()
                
                # 사용자가 충분하다고 생각하면 중단 가능
                if answer.lower() in ['충분', '충분해', '그만', '완료', 'done', 'skip']:
                    print("\n✅ 사용자가 대화를 종료했습니다.")
                    break
                    
                if not answer:
                    print("⚠️  답변을 입력해주세요. (충분하다면 '충분'이라고 입력하세요)")
                    continue
            
            # 대화 기록 저장
            self.conversation_history.append({
                "round": question_round,
                "question": question,
                "answer": answer
            })
            
            # 컨텍스트 업데이트
            current_context = self._update_context(current_context, question, answer)
            
            # 충분한 정보가 모였는지 확인
            if question_round >= 3:  # 최소 3번의 질문 후
                if self._is_sufficient_info(current_context):
                    print(f"\n✅ 충분한 정보가 수집되었습니다. (총 {question_round}번의 질문)")
                    break
        
        # 2단계: 정교화된 아이디어 생성 (Claude 사용 - 창의적)
        logger.info("🎨 Claude로 아이디어 합성 중...")
        refined_idea = self._synthesize_refined_idea(initial_idea, self.conversation_history)
        
        # 3단계: 세부 정보 추출 (Claude 사용 - 분석적)
        logger.info("📊 Claude로 세부 정보 추출 중...")
        extracted_details = self._extract_details(refined_idea, self.conversation_history)
        
        print("\n" + "="*80)
        print("✨ 아이디어 구체화 완료!")
        print("="*80)
        print(f"\n📌 정교화된 아이디어:\n{refined_idea}\n")
        
        result = {
            "initial_idea": initial_idea,
            "refined_idea": refined_idea,
            "conversation_history": self.conversation_history,
            "extracted_details": extracted_details
        }
        
        return result
    
    def _generate_question(self, context: str, round_num: int) -> str:
        """현재 컨텍스트를 바탕으로 다음 질문 생성 (GPT 사용 - 빠름)"""
        
        # 질문 영역 정의
        question_areas = {
            1: "타겟 독자와 목적",
            2: "수익성 극대화를 위한 최적 플랫폼 (네이버/티스토리/브런치/유튜브 등)",
            3: "30-31일 로테이션 가능한 에버그린 소주제 및 글감 방향성",
            4: "차별화 포인트와 경쟁 우위",
            5: "장기 지속 가능성 (연단위 반복 활용)"
        }
        
        area = question_areas.get(round_num, "추가 세부사항")
        
        prompt = f"""당신은 블로그 기획 전문가입니다.
사용자가 제시한 아이디어를 구체화하기 위해 질문을 생성하세요.

현재 컨텍스트:
{context}

현재 라운드: {round_num}
질문 영역: {area}

이전 대화 기록:
{self._format_conversation_history()}

위 정보를 바탕으로, 아이디어를 더 구체화할 수 있는 **1개의 핵심 질문**을 생성하세요.
질문은 구체적이고 실용적이어야 하며, 사용자가 쉽게 답할 수 있어야 합니다.

질문만 출력하세요 (설명 없이):"""

        # GPT 사용 (빠른 질문 생성)
        response = self.gpt_client.chat(prompt=prompt, max_tokens=200)
        
        return response.strip()
    
    def _generate_auto_answer(self, question: str, context: str) -> str:
        """자동 모드에서 질문에 대한 답변 자동 생성 (GPT 사용 - 테스트용)"""
        
        prompt = f"""현재 아이디어 컨텍스트:
{context}

질문: {question}

위 질문에 대해 구체적이고 실용적인 답변을 생성하세요.
답변은 1-3문장으로 간결하게 작성하세요.

답변만 출력하세요:"""

        # GPT 사용 (테스트용 자동 답변)
        response = self.gpt_client.chat(prompt=prompt, max_tokens=300)
        
        return response.strip()
    
    def _update_context(self, current_context: str, question: str, answer: str) -> str:
        """대화 내용을 반영하여 컨텍스트 업데이트"""
        return f"""{current_context}

Q: {question}
A: {answer}"""
    
    def _format_conversation_history(self) -> str:
        """대화 기록을 포맷팅"""
        if not self.conversation_history:
            return "없음"
        
        formatted = []
        for conv in self.conversation_history:
            formatted.append(f"Q{conv['round']}: {conv['question']}")
            formatted.append(f"A{conv['round']}: {conv['answer']}")
        
        return "\n".join(formatted)
    
    def _is_sufficient_info(self, context: str) -> bool:
        """충분한 정보가 모였는지 판단 (GPT 사용 - 빠른 판단)"""
        
        # 최소 3번의 대화가 있어야 함
        if len(self.conversation_history) < 3:
            return False
        
        # AI에게 충분성 판단 요청
        prompt = f"""다음 대화 내용을 분석하여, 블로그 아이디어를 구체화하기에 충분한 정보가 모였는지 판단하세요.

대화 컨텍스트:
{context}

판단 기준:
1. 타겟 독자가 명확한가?
2. 해결하려는 문제가 구체적인가?
3. 차별화 포인트가 있는가?
4. 콘텐츠 방향성이 명확한가?

충분하면 "YES", 더 필요하면 "NO"만 답하세요:"""

        # GPT 사용 (빠른 충분성 판단)
        response = self.gpt_client.chat(prompt=prompt, max_tokens=10)
        
        return "YES" in response.upper()
    
    def _synthesize_refined_idea(self, initial_idea: str, conversation: List[Dict]) -> str:
        """대화 내용을 종합하여 정교화된 아이디어 생성 (Claude 사용 - 창의적 합성)"""
        
        conversation_text = "\n".join([
            f"Q: {c['question']}\nA: {c['answer']}" 
            for c in conversation
        ])
        
        prompt = f"""당신은 블로그 기획 전문가입니다.
사용자의 초기 아이디어와 대화 내용을 종합하여 정교화된 아이디어를 생성하세요.

초기 아이디어: {initial_idea}

대화 내용:
{conversation_text}

위 정보를 바탕으로, 다음 형식으로 정교화된 아이디어를 작성하세요:

[블로그 주제]
- 핵심 주제: (한 문장)

[타겟 독자]
- (구체적으로)

[추천 플랫폼]
- 메인 플랫폼: (네이버/티스토리/브런치/인스타/유튜브 등 중 수익성 최적)
- 이유: (왜 이 플랫폼이 최적인지)
- 보조 플랫폼: (추가 활용 가능한 플랫폼)

[30일 에버그린 콘텐츠 전략]
- 로테이션 가능 소주제: (계절/트렌드 무관하게 연중 활용 가능한 주제 3-5개)
- 글감 재활용 방법: (어떻게 매년 반복 활용할지)

[차별화 포인트]
- (2-3개 항목)

[수익화 전략]
- (광고/제휴/상품 등)

[기대 효과]
- (간단히)

위 형식을 정확히 지켜서 작성하세요:"""

        # Claude 사용 (창의적이고 자연스러운 아이디어 합성)
        response = self.hybrid_client.chat(
            prompt=prompt, 
            max_tokens=1000,
            task_type="creative"  # Claude 사용
        )
        
        return response.strip()
    
    def _extract_details(self, refined_idea: str, conversation: List[Dict]) -> Dict[str, Any]:
        """정교화된 아이디어에서 구조화된 세부 정보 추출 (Claude 사용 - 분석적)"""
        
        conversation_text = "\n".join([
            f"Q: {c['question']}\nA: {c['answer']}" 
            for c in conversation
        ])
        
        prompt = f"""다음 정교화된 아이디어에서 구조화된 정보를 추출하세요.

정교화된 아이디어:
{refined_idea}

대화 내용:
{conversation_text}

다음 JSON 형식으로 정보를 추출하세요:
{{
    "main_topic": "핵심 주제 (한 문장)",
    "target_audience": "타겟 독자 (구체적으로)",
    "recommended_platform": {{
        "primary": "메인 플랫폼 (네이버/티스토리/브런치 등)",
        "reason": "선정 이유",
        "secondary": ["보조 플랫폼1", "보조 플랫폼2"]
    }},
    "evergreen_strategy": {{
        "rotation_topics": ["30일 로테이션 소주제1", "소주제2", "소주제3"],
        "reusability": "글감 재활용 방법 (연단위 반복 활용 전략)"
    }},
    "key_problems": ["해결할 문제 1", "해결할 문제 2"],
    "differentiators": ["차별화 포인트 1", "차별화 포인트 2"],
    "content_pillars": ["콘텐츠 기둥 1", "콘텐츠 기둥 2", "콘텐츠 기둥 3"],
    "content_style": "콘텐츠 스타일 (예: 실용적 가이드, 경험 공유 등)",
    "monetization_strategy": {{
        "methods": ["수익화 방법1", "수익화 방법2"],
        "potential": "상/중/하",
        "reason": "근거"
    }}
}}

JSON만 출력하세요 (코드 블록 없이):"""

        # Claude 사용 (정교한 분석 및 추출)
        response = self.hybrid_client.chat(
            prompt=prompt, 
            max_tokens=1000,
            task_type="analytical"  # Claude 사용
        )
        
        # JSON 파싱
        import json
        try:
            # 코드 블록 제거
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            details = json.loads(response.strip())
            return details
        except Exception as e:
            logger.warning(f"JSON 파싱 실패: {e}")
            return {
                "main_topic": refined_idea.split('\n')[0] if refined_idea else "",
                "target_audience": "",
                "recommended_platform": {
                    "primary": "네이버 블로그",
                    "reason": "기본값",
                    "secondary": []
                },
                "evergreen_strategy": {
                    "rotation_topics": [],
                    "reusability": ""
                },
                "key_problems": [],
                "differentiators": [],
                "content_pillars": [],
                "content_style": "",
                "monetization_strategy": {
                    "methods": [],
                    "potential": "중",
                    "reason": ""
                }
            }


if __name__ == "__main__":
    # 테스트
    refiner = IdeaRefinerNode()
    
    # 대화형 모드 테스트
    initial = input("💡 블로그 아이디어를 입력하세요: ").strip()
    if not initial:
        initial = "가족 여행 블로그"
        print(f"(기본값 사용: {initial})")
    
    # auto_mode=False로 실제 대화형 모드 실행
    result = refiner.refine_interactive(initial, auto_mode=False)
    
    print("\n\n" + "="*80)
    print("📊 최종 결과")
    print("="*80)
    print(f"\n초기 아이디어: {result['initial_idea']}")
    print(f"\n정교화된 아이디어:\n{result['refined_idea']}")
    print(f"\n추출된 세부 정보:")
    import json
    print(json.dumps(result['extracted_details'], ensure_ascii=False, indent=2))
