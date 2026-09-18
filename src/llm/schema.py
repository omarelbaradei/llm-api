from langchain_core.prompts import ChatPromptTemplate


template = ChatPromptTemplate.from_messages([
    #("system","{system_message}")
    ("human",'''the output must follow the format instruction and must be json structured and the confidence key must be within 0 and 1 based on model's confidence
    input:{prompt} format instruction:{format_instruction}''')
])



