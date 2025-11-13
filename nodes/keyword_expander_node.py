# nodes/keyword_expander_node.py
import json
from typing import Dict, Any, List

from utils.logger import get_logger
from utils.llm_client import LLMClient
from utils.naver_datalab import NaverDataLabClient

logger = get_logger("KeywordExpanderNode")


class KeywordExpanderNode:
    """
    Step2: 키워드 확장 노드
    - LSI 키워드 생성
    - 검색량 수집 (네이버 데이터랩 API or LLM Fallback)
    - 키워드 난이도/우선순위 스코어링
    - 키워드 Cluster 생성
    """

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.datalab = NaverDataLabClient()

    def expand(self, topic_json: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("KeywordExpanderNode 시작")

        main_kw = topic_json.get("main_keywords", [])
        sub_kw = topic_json.get("sub_keywords", [])
        combined_kw = list(set(main_kw + sub_kw))

        # 1) LSI 확장 프롬프트 생성
        prompt = self._build_prompt(combined_kw)

        try:
            raw_output = self.llm.chat(prompt)
            parsed = self._safe_parse_json(raw_output)
        except Exception as e:
            logger.exception("LLM keyword 생성 실패")
            raise e

        expanded_keywords = parsed["expanded_keywords"]

        # 2) 검색량 조회
        volume_data = self.datalab.get_volume(expanded_keywords)

        if volume_data["fallback"]:
            # LLM 기반 추정값
            volume = self._fake_volume(expanded_keywords)
        else:
            volume = self._parse_datalab_volume(volume_data["result"])

        # 3) 난이도 스코어링
        difficulty_scores = self._difficulty_scoring(expanded_keywords)

        # 4) Cluster 생성
        clusters = self._cluster_keywords(expanded_keywords)

        result = {
            "topic": topic_json["topic"],
            "expanded_keywords": expanded_keywords,
            "search_volume": volume,
            "difficulty_score": difficulty_scores,
            "clusters": clusters,
        }

        logger.info("KeywordExpanderNode 완료")
        return result

    def _build_prompt(self, keywords: List[str]) -> str:
        return f"""
다음 키워드 목록을 기반으로 LSI/롱테일 키워드를 생성해줘.

입력 키워드:
{keywords}

출력 JSON 스키마:
{{
  "expanded_keywords": []
}}

조건:
1. 총 개수 20~40개
2. 중복 제거
3. JSON 외 텍스트 금지
        """

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            cleaned = text[start:end]
            return json.loads(cleaned)
        except Exception:
            logger.error("JSON 파싱 실패")
            logger.error(text)
            raise ValueError("LLM 응답 JSON 파싱 실패")

    def _fake_volume(self, keywords: List[str]) -> Dict[str, int]:
        """데이터랩 미연결 시 LLM 기반 추정 대신 단순 랜덤 값 생성"""
        volume = {}
        for kw in keywords:
            volume[kw] = len(kw) * 1000 + 300
        return volume

    def _parse_datalab_volume(self, data: Dict[str, Any]) -> Dict[str, int]:
        """네이버 데이터랩 트렌드 값 평균"""
        result = {}
        try:
            for group in data["results"]:
                kw = group["title"]
                vals = [v["ratio"] for v in group["data"]]
                result[kw] = int(sum(vals) / len(vals))
            return result
        except Exception:
            logger.error("데이터랩 파싱 실패. fallback 활용")
            return self._fake_volume([g["title"] for g in data["results"]])

    def _difficulty_scoring(self, keywords: List[str]) -> Dict[str, int]:
        """간단 난이도 점수"""
        score = {}
        for kw in keywords:
            score[kw] = min(100, max(1, len(kw) * 5))
        return score

    def _cluster_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """간단한 단어 기반 클러스터링"""
        clusters = {"자동화": [], "운영": [], "AI": [], "기타": []}
        for kw in keywords:
            if "자동" in kw:
                clusters["자동화"].append(kw)
            elif "운영" in kw:
                clusters["운영"].append(kw)
            elif "AI" in kw or "GPT" in kw:
                clusters["AI"].append(kw)
            else:
                clusters["기타"].append(kw)
        return clusters
