"""
Step 4 빠른 테스트: Day 1 생성
"""

import json
import os
import sys

# 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.seo_content_writer_node import SEOContentWriterNode

# 입력 로드
with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
    pipeline_result = json.load(f)
    content_plan_data = pipeline_result.get("content_plan", {})
    content_plan = content_plan_data.get("30_days_plan", [])
    serp_result = pipeline_result.get("serp_result", {})

with open("outputs/tone_style_guide.json", "r", encoding="utf-8") as f:
    tone_guide = json.load(f)

print("\n" + "="*80)
print("📝 Step 4 테스트: Day 1 SEO 콘텐츠 생성")
print("="*80)
print(f"\n주제: {content_plan[0].get('title', 'N/A')}")
print(f"카테고리: {content_plan[0].get('category', 'N/A')}")
print(f"\n예상 비용: ₩35")
print(f"예상 시간: 30초")

# 생성
writer = SEOContentWriterNode()
results = writer.generate_all(
    content_plan=content_plan,
    tone_guide=tone_guide,
    serp_context=serp_result,
    start_day=1,
    end_day=1
)

# 저장
output_dir = "outputs/content"
os.makedirs(output_dir, exist_ok=True)

for content in results:
    day_num = content.get("day", 0)
    output_path = os.path.join(output_dir, f"day{day_num:02d}_content.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 저장 완료: {output_path}")
    print(f"📊 글자 수: {content.get('full_text_length', 0)}자")
    print(f"📝 섹션 수: {len(content.get('sections', []))}개")

print("\n" + "="*80)
print("✅ Day 1 생성 완료!")
print("="*80)
