from llm.client import load_active_llm

model = load_active_llm()

res = model.bind_tools

print(res)