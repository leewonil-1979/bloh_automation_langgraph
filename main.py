from dotenv import load_dotenv
load_dotenv()

import json
from nodes.topic_refiner_node import TopicRefinerNode

if __name__ == "__main__":
    node = TopicRefinerNode()
    result = node.refine("블로그 자동화 시스템 만드는 법")
    print(json.dumps(result, indent=2, ensure_ascii=False))
