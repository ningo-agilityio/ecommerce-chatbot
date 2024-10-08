from app.chatbot.agent_executor import run_with_memory
response = run_with_memory('What is LangChain?', None)
print(response['output'])