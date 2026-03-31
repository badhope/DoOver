from llm.service import get_model
model = get_model()
result = model.invoke("...")

print(result)