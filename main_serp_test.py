# main_serp_test.py
from dotenv import load_dotenv
load_dotenv()

import json
from nodes.serp_collector_node import SERPCollectorNode

if __name__ == "__main__":
    node = SERPCollectorNode()
    result = node.collect("블로그 자동화")
    print(json.dumps(result, ensure_ascii=False, indent=2))
