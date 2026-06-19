from fastapi import FastAPI
from pydantic import BaseModel
from app.logic import is_eligible_for_loan, is_password_strong

app = FastAPI()


class Applicant(BaseModel):
    income: float
    age: int
    employment_status: str


class PasswordData(BaseModel):
    password: str


@app.post('/loan-eligibility')
def check_eligibility(applicant: Applicant):
    eligibility = is_eligible_for_loan(
        income=applicant.income,
        age=applicant.age,
        employment_status=applicant.employment_status
    )
    return {'eligible': eligibility}


@app.post('/password-strength')
def check_password_strength(data: PasswordData):
    strong = is_password_strong(data.password)
    return {'strong': strong}