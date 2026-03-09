from fastapi import FastAPI, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from core.database import engine, get_db, SessionLocal
import models.document as models
import PyPDF2
import io
from services.llm_service import summarize_in_background

# This line creates the tables in SQLite when the app starts!
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "API is running happily!"}

@app.post("/upload")
async def upload_document(
    # 1. We expect a file from the user
    file: UploadFile = File(...), 
    # 2. We need a temporary database session to save the file
    db: Session = Depends(get_db),

    background_tasks: BackgroundTasks = BackgroundTasks()
):
    # Step A: Read the actual text inside the file the user uploaded
    content = await file.read()

    text_content = "" # We will store the final extracted text here
    # Step B: Check the file extension to see how we should process it
    if file.filename.endswith(".pdf"):
        # 1. We need to trick PyPDF2 into thinking our raw bytes are a real file on the hard drive.
        # We use io.BytesIO for this.
        pdf_file = io.BytesIO(content)
        
        # 2. Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # 3. Loop through every page in the PDF and extract the text
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"
            
    elif file.filename.endswith(".txt"):
        # If it's a text file, decode it just like we did before!
        text_content = content.decode("utf-8")
        
    else:
        # What if they upload an image or a word doc?
        # We should probably return an error!
        return {"error": "Only .txt and .pdf files are supported right now."}
    # Step C: Create a new row for our database using the Model we built!
    # Notice we don't pass 'id' because SQLite generates that automatically.
    # We also don't pass 'summary_text' because we haven't summarized it yet.
    new_doc = models.Document(
        filename=file.filename,
        original_text=text_content,
        status="pending"
    )
    
    # Step D: Actually save it to the database
    db.add(new_doc)      # Add it to the session
    db.commit()          # Commit (save) the changes permanently
    db.refresh(new_doc)  # Refresh it so our 'new_doc' variable gets the brand new 'id'
    background_tasks.add_task(summarize_in_background, new_doc.id, SessionLocal)
    # Step E: Return a success message back to the user!
    return {
        "message": "File uploaded successfully!", 
        "document_id": new_doc.id, 
        "status": new_doc.status
    }


@app.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    
    if not doc:
        return {"error": "Document not found!"}
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,           # "pending" / "processing" / "completed" / "failed"
        "summary": doc.summary_text     # Will be None until completed
    }
