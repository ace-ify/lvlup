import os
from dotenv import load_dotenv

# Load those environment variables from the .env file!
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Initialize the LLM Object
# We pass the real model name here! 
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY") 
)

# 2. Define the Prompt
prompt = ChatPromptTemplate.from_template(
    """
    You are an expert academic assistant. 
    Please summarize the following text into exactly 3 bullet points.
    
    Text to summarize:
    {text}
    """
)

# 3. Define the Output Parser
# This just makes sure we get a normal string back instead of a weird AI message object
output_parser = StrOutputParser()

# 4. Create the Chain
chain = prompt | llm | output_parser

# # 5. The Function (MUST use async def to not block FastAPI)
# async def summarize_text(text: str) -> str:
#     """Sends text to the LLM and returns the summary."""
#     try:
#         # Notice we use `ainvoke` (Async Invoke) because this is an async function! 
#         summary = await chain.ainvoke({"text": text})
#         return summary
#     except Exception as e:
#         # If something goes wrong, we will return the error as a string for now.
#         return f"Error calling LLM: {str(e)}"

from sqlalchemy.orm import Session

def summarize_in_background(document_id: int, db_session_factory):
    """
    This runs in a background thread AFTER the response is sent.
    We create a fresh DB session here because the original request's session closes after response.
    """
    # Create a brand new DB session just for this background task
    db: Session = db_session_factory()
    try:
        # 1. Fetch the doc and mark it as "processing"
        from models.document import Document
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return
        
        doc.status = "processing"
        db.commit()
        
        # 2. Call the LLM (synchronous invoke here, NOT ainvoke!)
        summary = chain.invoke({"text": doc.original_text})
        
        # 3. Save result
        doc.summary_text = summary
        doc.status = "completed"
        db.commit()
        print(f"✅ Document {document_id} summarized successfully!")
        
    except Exception as e:
        # If something goes wrong, mark it as failed
        doc.status = "failed"
        db.commit()
        print(f"❌ Background task failed for doc {document_id}: {e}")
    finally:
        db.close()  # Always close the session!
