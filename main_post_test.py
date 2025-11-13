# main_post_test.py
from dotenv import load_dotenv
load_dotenv()

import json
from nodes.topic_refiner_node import TopicRefinerNode
from nodes.keyword_expander_node import KeywordExpanderNode
from nodes.serp_collector_node import SERPCollectorNode
from nodes.post_writer_node import PostWriterNode

if __name__ == "__main__":
    step1 = TopicRefinerNode()
    topic = step1.refine("블로그 자동화 시스템 만드는 법")

    step2 = KeywordExpanderNode()
    kws = step2.expand(topic)

    step3 = SERPCollectorNode()
    serp = step3.collect("블로그 자동화")

    step4 = PostWriterNode()
    post = step4.write(topic, kws, serp)

    print(json.dumps(post, ensure_ascii=False, indent=2))
