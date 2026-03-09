from sqlalchemy import Column, Integer, String, Text
from core.database import Base

class Document(Base):
    # This specifically tells SQLAlchemy the actual name of the table in the database
    __tablename__ = "documents"

    # id: The unique Primary Key for each document (1, 2, 3...)
    # index=True makes searching for IDs much faster
    id = Column(Integer, primary_key=True, index=True)
    
    # filename: e.g., "my_essay.pdf"
    filename = Column(String, index=True)
    
    # status: We will use this to track progress (e.g., "pending", "processing", "completed", "failed")
    # By default, when a new row is created, the status starts as "pending"
    status = Column(String, default="pending")
    
    # original_text: The full text we extract from the document
    # Using 'Text' instead of String because it could be thousands of characters long
    original_text = Column(Text, nullable=True) 
    
    # summary_text: The final LLM summary. 
    # nullable=True means it is perfectly fine if this is empty when the row is first created.
    summary_text = Column(Text, nullable=True)
