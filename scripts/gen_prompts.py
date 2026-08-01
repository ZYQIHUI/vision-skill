#!/usr/bin/env python3
"""Generate assets/prompts.json — run once to create the prompt template file."""
import json, os

data = {
  "fast_comprehensive": {
    "description": "单次综合调用,一次提取全部六个理解维度",
    "prompt": "你是一个严谨的视觉分析专家。请对这张图片进行全面深入的分析,严格按照下方 JSON schema 返回结果,不要增减字段,不要包裹 markdown 代码块标记。\n\n要求包含以下字段:\n{\n  \"scene_graph\": {\n    \"objects\": [{\"id\": 1, \"name\": \"\", \"attributes\": []}],\n    \"relationships\": [{\"subject\": 1, \"predicate\": \"\", \"object\": 2}],\n    \"scene_type\": \"\",\n    \"setting\": \"\"\n  },\n  \"spatial_layout\": \"详细描述各物体的空间位置关系(左/中/右, 上/中/下, 近/远, 前景/背景)\",\n  \"extracted_text\": \"图片中所有可见文字,无文字则为空字符串\",\n  \"description\": \"自然语言客观描述图片内容,只陈述直接可见的主干:主体、动作、环境,不做推测\",\n  \"context\": {\n    \"what_happening\": \"正在发生什么(基于可见证据的最小推断)\",\n    \"time_season\": \"时间/季节推断,若无法判断则填无法判断\",\n    \"cultural_context\": \"文化或地理背景,若无明显线索则填无明显文化或地理特征\",\n    \"before_event\": \"之前可能发生了什么,若无法推断则填无足够线索\",\n    \"after_event\": \"之后可能发生什么,若无法推断则填无足够线索\"\n  },\n  \"emotion\": {\n    \"mood\": \"整体情绪\",\n    \"visual_cues\": \"哪些视觉元素(光线、色彩、构图)营造了这种情绪\",\n    \"evoked_feeling\": \"唤起观者的感受\"\n  },\n  \"reasoning_chain\": {\n    \"observations\": \"直接观察到的事实(只描述客观可见的)\",\n    \"inferences\": \"从事实推断出的结论(明确标注为推断)\",\n    \"background_knowledge\": \"相关背景知识,若无则填无\",\n    \"conclusion\": \"最终结论\",\n    \"alternatives\": \"替代解读,若无则填无明显替代解读\"\n  }\n}\n\n遵循以下约束:\n1. observations 只填直接可见的事实,不夹杂推测;推测全部放 inferences。\n2. 所有推断字段必须基于可见证据,无法推断的字段如 schema 所示填无法判断或无足够线索,不要编造。\n3. 这不是以图生文创作,而是客观分析;不要使用修辞或主观抒发。\n4. 只返回有效 JSON,第一个字符必须是 {,最后一个字符必须是 }。",
    "few_shot": {
      "description": "给模型一个最小可行例答,稳定 schema 跟随(尤其对中文模型的 JSON 遵从度)",
      "example_input": "一只狗站在湿漉漉的路面上,嘴里叼着一把伞",
      "example_output": {
        "scene_graph": {
          "objects": [
            {"id": 1, "name": "狗", "attributes": ["嘴叼伞", "站立"]},
            {"id": 2, "name": "路面", "attributes": ["湿", "反光"]},
            {"id": 3, "name": "伞", "attributes": ["被叼着"]}
          ],
          "relationships": [
            {"subject": 1, "predicate": "站在", "object": 2},
            {"subject": 1, "predicate": "叼着", "object": 3}
          ],
          "scene_type": "街景",
          "setting": "雨后街道"
        },
        "spatial_layout": "狗位于画面中央,路面在底部前景,伞在狗嘴前方略微偏上。",
        "extracted_text": "",
        "description": "一只狗站在湿润反光的路面上,嘴里叼着一把伞,背景为街道。",
        "context": {
          "what_happening": "雨后,一只狗叼着伞站在路面上",
          "time_season": "无法判断具体时间季节,仅由湿地面推断刚下过雨",
          "cultural_context": "无明显文化或地理特征",
          "before_event": "无足够线索",
          "after_event": "无足够线索"
        },
        "emotion": {
          "mood": "略带诙谐",
          "visual_cues": "湿路反光与狗叼伞的反常组合",
          "evoked_feeling": "好奇与轻微的幽默感"
        },
        "reasoning_chain": {
          "observations": "路面湿且反光;一只狗站立;狗嘴里叼着一把伞",
          "inferences": "刚下过雨;伞本应由人使用,被狗叼着是反常情景",
          "background_knowledge": "无",
          "conclusion": "雨后街景中,一只狗叼着伞站立,构成略带诙谐的画面",
          "alternatives": "也可能是拍摄者主动把伞放进狗嘴摆拍"
        }
      }
    }
  },
  "scene_graph": {
    "description": "场景图提取",
    "prompt": "分析这张图片,生成场景图,输出有效 JSON。\n格式:\n{\n  \"objects\": [\n    {\"id\": 1, \"name\": \"对象名称\", \"attributes\": [\"属性1\", \"属性2\"]}\n  ],\n  \"relationships\": [\n    {\"subject\": 1, \"predicate\": \"空间关系\", \"object\": 2}\n  ],\n  \"scene_type\": \"场景类型\",\n  \"setting_details\": \"环境简述\"\n}\n只返回 JSON,第一个字符必须是 {。"
  },
  "spatial": {
    "description": "空间布局描述",
    "prompt": "详细描述这张图片的空间布局:\n1. 每个主要物体的位置(左/中/右,上/中/下)\n2. 物体间的相对距离(近/远,前景/背景)\n3. 深度和透视线索\n4. 整体构图和取景\n要精确描述空间关系,只基于可见证据。"
  },
  "text_ocr": {
    "description": "文字提取",
    "prompt": "提取图片中所有可见文字。包括标志、标签、屏幕内容、文档、手写笔记。保留原始语言。如果没有文字,回答空字符串。只返回提取的文字。"
  },
  "context": {
    "description": "上下文推断",
    "prompt": "分析这张图片的上下文:\n1. 正在发生什么?描述主要动作或事件(基于可见证据的最小推断)。\n2. 这暗示了什么时间/季节/年代?若无法判断请直接说明。\n3. 暗含什么文化或地理背景?若无明显线索请直接说明。\n4. 在这一刻之前可能发生了什么?若无法推断请直接说明。\n5. 接下来可能发生什么?若无法推断请直接说明。\n明确区分观察和推断。无法确定时直说,不要编造。"
  },
  "emotion": {
    "description": "情感氛围分析",
    "prompt": "分析这张图片的情感和氛围:\n1. 整体情绪(如紧张、欢乐、宁静、忧郁)\n2. 哪些视觉元素(光线、色彩、构图)营造了这种情绪\n3. 画面中人物的情绪状态\n4. 这张图片唤起观者什么感受\n具体说明哪些视觉线索导致了你的结论。"
  },
  "reasoning": {
    "description": "因果推理链",
    "prompt": "对这张图片生成思维链推理:\n第一步:关键可观察事实是什么?(只描述直接可见的)\n第二步:从这些事实可以推断出什么?(明确标注为推断)\n第三步:什么背景知识是相关的?(若无则写无)\n第四步:可以得出什么结论?\n第五步:存在哪些替代解读?\n区分观察和推断。无法确定时直说,不要编造。"
  },
  "query": {
    "description": "VQA 事实复核模板",
    "template": "你是一个严谨的视觉核查员。精确、简洁地回答关于这张图片的问题。\n\n问题:{question}\n\n要求:\n- 只基于图片中可见的内容回答\n- 如果图片信息不足以回答,明确说无法从图片中确定,不要编造\n- 是非题先回答是或否,再解释\n- 计数题给出确切数字\n- 空间问题要具体描述位置\n- 给出视觉证据支持你的回答\n- 明确区分直接看到和据此推断"
  }
}

out = os.path.join(os.path.dirname(__file__), "..", "assets", "prompts.json")
out = os.path.normpath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"written: {out} ({os.path.getsize(out)} bytes)")
