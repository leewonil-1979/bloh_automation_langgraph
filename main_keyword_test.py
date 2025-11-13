# main_keyword_test.py
from dotenv import load_dotenv
load_dotenv()

import json
from nodes.topic_refiner_node import TopicRefinerNode
from nodes.keyword_expander_node import KeywordExpanderNode

if __name__ == "__main__":
    step1 = TopicRefinerNode()
    topic_json = step1.refine("블로그 자동화 시스템 만드는 법")

    step2 = KeywordExpanderNode()
    expanded = step2.expand(topic_json)

    print(json.dumps(expanded, ensure_ascii=False, indent=2))
