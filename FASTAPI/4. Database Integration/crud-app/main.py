from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from typing import List
import models, crud, schemas

# Initialize database tables on application start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee API (Production-Ready)",
    description="A highly-optimized and secure CRUD API for managing employee directories.",
    version="1.0.0"
)

# Database session manager (Dependency Injection)
# Yields a database session to path operations and guarantees cleanup.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. CREATE AN EMPLOYEE (POST)
# Returns 201 Created on success.
@app.post(
    '/employees',
    response_model=schemas.EmployeeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee"
)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = crud.create_employee(db, employee)
    if db_employee is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered or transaction failed due to conflict."
        )
    return db_employee

# 2. GET ALL EMPLOYEES (GET)
@app.get(
    '/employees',
    response_model=List[schemas.EmployeeOut],
    summary="Get all employees list"
)
def get_employees(db: Session = Depends(get_db)):
    return crud.get_employees(db)

# 3. GET A SPECIFIC EMPLOYEE (GET by ID)
@app.get(
    '/employees/{emp_id}',
    response_model=schemas.EmployeeOut,
    summary="Get employee by ID"
)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db, emp_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found."
        )
    return employee

# 4. UPDATE AN EMPLOYEE (PUT by ID)
@app.put(
    '/employees/{emp_id}',
    response_model=schemas.EmployeeOut,
    summary="Update employee by ID"
)
def update_employee(emp_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_employee = crud.update_employee(db, emp_id, employee)
    if db_employee is None:
        # Occurs if employee ID doesn't exist OR if user attempts to update email to one that is already registered
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee not found, or email is already taken by another record."
        )
    return db_employee

# 5. DELETE AN EMPLOYEE (DELETE by ID)
@app.delete(
    '/employees/{emp_id}',
    response_model=dict,
    summary="Delete employee by ID"
)
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    employee = crud.delete_employee(db, emp_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found."
        )
    return {"detail": "Employee deleted successfully."}


