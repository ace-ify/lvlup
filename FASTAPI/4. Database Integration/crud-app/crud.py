from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models, schemas

def get_employees(db: Session):
    """
    Fetch all employee records from the database.
    """
    return db.query(models.Employee).all()

def get_employee(db: Session, emp_id: int):
    """
    Retrieve a specific employee by their ID.
    """
    return db.query(models.Employee).filter(models.Employee.id == emp_id).first()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    """
    Create a new employee record.
    Uses try-except blocks to catch duplicate email constraints (IntegrityError).
    """
    # 1. Check if email is already taken
    existing = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing:
        return None  # Will be caught by controller to raise HTTP 400

    db_employee = models.Employee(name=employee.name, email=employee.email)
    try:
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    except IntegrityError:
        # In case of concurrent race condition write failures, rollback state cleanly
        db.rollback()
        return None

def update_employee(db: Session, emp_id: int, employee: schemas.EmployeeUpdate):
    """
    Update an existing employee record by ID.
    Queries the database first to ensure the employee exists before committing.
    """
    # 1. Locate the existing record
    db_employee = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    
    if db_employee:
        db_employee.name = employee.name
        db_employee.email = employee.email
        try:
            db.commit()
            db.refresh(db_employee)
            return db_employee
        except IntegrityError:
            # Handles duplicate email constraint collisions on update
            db.rollback()
            return None
    return None

def delete_employee(db: Session, emp_id: int):
    """
    Delete an employee record by ID.
    """
    db_employee = db.query(models.Employee).filter(models.Employee.id == emp_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return db_employee
    return None