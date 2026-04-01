from llm.service import get_model
from typing_extensions import TypedDict, Annotated
from graph.prompts import prompt_template
model = get_model()
user_input = "我小时候在乡下长大，后来考上了北京的大学，毕业后去了上海工作。我和前女友分手是因为她要去国外深造。"
world_info = {"location": "中国", "age_range": "20-30"} # 假设的背景信息
prompt = prompt_template.format(raw_input=user_input, world_info=world_info)
chunks = []
for chunk in model.stream(prompt):
        text = chunk.content if hasattr(chunk, "content") else str(chunk)
        chunks.append(text)
        print(text,end="",flush=True)

print("========")
final_text = "".join(chunks)
print(final_text)