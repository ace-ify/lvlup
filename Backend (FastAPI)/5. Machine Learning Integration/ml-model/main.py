"""
=========================================================================================
📘 MODULE 5 SUMMARY & PRODUCTION STUDY GUIDE (ML MODEL SERVING)
=========================================================================================

💡 KEY ARCHITECTURAL CONCEPTS & Q/A:

1. Why does startup run before 'yield' and shutdown after 'yield'?
   - CONCEPT: Context Manager Protocol & Generator Functions.
   - EXPLANATION: FastAPI runs the lifespan function inside an `async with` block under the 
     hood. 
     * When the server boots up, Python executes code up to the `yield` statement (Startup stage).
     * Python then pauses the generator function at `yield`, starts the server, and handles API routes.
     * When the server shuts down (e.g., Ctrl+C), Python resumes execution *after* the `yield` 
       statement, running the cleanup code (Shutdown stage).

2. Why not just load the model globally once at the file scope level?
   - EXPLANATION: If loaded at the global file scope level, any missing or corrupt model file 
     crashes the entire python process during import time before uvicorn can even boot or 
     log warnings gracefully. Lifespan event handlers isolate this startup step, and 
     wrapping it in a `try...except` block allows the server to boot successfully and 
     respond with a clean "503 Service Unavailable" error instead of crashing.

3. Why is 'request.app.state.model' evaluated inside each route handler?
   - EXPLANATION: Because `app.state` is empty at global scope instantiation time. The model 
     object only exists inside `app.state` *after* the server completes its startup phase. 
     The `Request` object gives route handlers dynamic access to the active running 
     application state instance at call time.

4. Why does 'make_prediction' take the model as a parameter now?
   - CONCEPT: Dependency Injection & Decoupling.
   - EXPLANATION: To keep predict.py clean and stateless. Because predict.py no longer loads 
     the model globally, it has no direct reference to the model. We pass the loaded model 
     directly from main.py's state locker down to predict.py's helper function as a parameter.
=========================================================================================
"""

from fastapi import FastAPI, Request, HTTPException, status
from predict import make_prediction, make_batchpredictions
from schemas import InputSchema, OutputSchema
from typing import List
from contextlib import asynccontextmanager
import joblib

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs ONCE at startup

    print("🚀 [STARTUP] Safely loading model.joblib into memory...")
    try:
        app.state.model = joblib.load("model.joblib")
        print("✅ [STARTUP] Model loaded successfully!")
    except FileNotFoundError:
        # Catch the exception: Log it but allow the server to boot
        print("⚠️ [STARTUP WARNING] model.joblib file not found! API will boot but prediction endpoints will be disabled.")
        app.state.model = None
    yield
    # This runs ONCE at shutdown
    print("🧹 [SHUTDOWN] Cleaning up model memory references...")
    app.state.model = None

app = FastAPI(title='House Price Predictor', lifespan=lifespan)

@app.get('/')
def index():
    return {'message':'Welcome to the House Price Predictor API'}

@app.post('/prediction', response_model=OutputSchema)
def predict(request: Request, user_input: InputSchema):
    model = request.app.state.model
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is currently unavailable on the server."
        )
    prediction = make_prediction(model, user_input.model_dump())
    return OutputSchema(predicted_price=round(prediction, 2))

@app.post('/batch-predictions', response_model=List[OutputSchema])
def batch_predict(request: Request, batch_input: List[InputSchema]):
    model = request.app.state.model
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning model is currently unavailable on the server."
        )
    predictions = make_batchpredictions(
        model, 
        [input.model_dump() for input in batch_input]
    )
    return [OutputSchema(predicted_price=round(prediction, 2)) for prediction in predictions]
