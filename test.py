import getpass
import os


if not os.environ.get("AIVERDE_API_KEY"):
  os.environ["AIVERDE_API_KEY"] = getpass.getpass("Enter AI-VERDE API key: ")
api_key = os.environ["AIVERDE_API_KEY"]


from langchain_litellm import ChatLiteLLM
from langchain.messages import HumanMessage, SystemMessage, AIMessage

llm = ChatLiteLLM(
    model="litellm_proxy/js2/gpt-oss-120b",
    api_key=api_key,
    api_base="https://llm-api.cyverse.ai",
    )








messages = [
  SystemMessage(content="You are an assistant, keep answers concise.")
]


print("Enter prompt or ctrl+c to quit:")

while(True):
  user_input = input()
  messages.append(HumanMessage(content=user_input))
  response = llm.invoke(messages)

  print("\n" + response.content + "\n")
  
  messages.append(response)




  
  



