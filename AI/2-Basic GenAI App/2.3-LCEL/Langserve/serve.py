from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from langserve import add_routes
from dotenv import load_dotenv
load_dotenv()

groq_api_key=os.getenv("GROQ_API_KEY")
model=ChatGroq(model="openai/gpt-oss-120b",groq_api_key=groq_api_key)

system_template="Tell a joke on {topic}."
prompt_template=ChatPromptTemplate.from_messages([
    ('system',system_template),
    ('user','{topic}')
])

parser=StrOutputParser()

chain=prompt_template|model|parser

app=FastAPI(
    title='LangJoke',
    version='1.0',
    description='Lang will joke here'
)

add_routes(
    app,
    chain,
    path="/chain"
)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=7000)