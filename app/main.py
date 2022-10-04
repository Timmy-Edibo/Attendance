from fastapi import FastAPI, Depends, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session
from .database import engine
from datetime import date
from datetime import datetime

from . import models
models.Base.metadata.create_all(bind=engine)

from . database import SessionLocal, engine
from .schemas import AttendanceForm, RegisterForm, AttendanceByDate


#For email validation
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import EmailStr, error_wrappers


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Stemlab Attendance System V-001")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["set-cookie"],
)    



# @app.exception_handler(RequestValidationError)
# async def format_validation_error_as_rfc_7807_problem_json(request: Request, exc: error_wrappers.ValidationError):
#     status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
#     content = {"type": "/errors/unprocessable_entity", 
#     "title": "Unprocessable Entity", 
#     "status": status_code, 
#     "detail": "The request is invalid.",
#     "instance": request.url.path, 
#     "issues": jsonable_encoder(exc.errors()[0]["msg"])}

#     return JSONResponse(content, status_code=status_code)


@app.post("/register", tags=["Register"])
async def register(form: RegisterForm, db: Session = Depends(get_db)):
    add_attendance =form.__dict__
    user_extract = add_attendance["qrcode"]

    add_attendance = user_extract.split(" ")
    email = add_attendance[1]
    phone_number = add_attendance[2]
    role = add_attendance[3]

    try:
        user_form = models.Users(email=email, phone_number=phone_number, role=role)
        
        db.add(user_form)
        db.commit()
        db.refresh(user_form) 
    except IntegrityError as e:

        db.rollback()
        if "users_phone_number_key" in str(e):
            raise HTTPException(status_code=401, detail="User with phone number already exist") from e

        if "users_email_key" in str(e):
            raise HTTPException(status_code=401, detail="User with email already exist") from e
    return user_form
        


# from datetime import time
# print(datetime.now().time().hour)
@app.post("/attendance", tags=["Attendance"])
async def make_attendance(form:AttendanceForm, db: Session = Depends(get_db)):
    
    #Getting current date and time
    todays_date = date.today()
    current_time = datetime.now().time().hour

    #Getting qrcode field
    user_info_extract = form.qrcode
    
    #Extraccting user info from qrcode
    add_attendance = user_info_extract.split(" ")
    email = add_attendance[1]
    name = add_attendance[0]

    check_email = db.query(models.Users).filter(models.Users.email==email).first()
    if not check_email:
        raise HTTPException(status_code =404, detail="User with this email address not found")

    if check_signedIn := db.query(models.Attendance).filter(
        models.Attendance.email == email).filter(models.Attendance.created_at == todays_date).first():
        raise HTTPException(status_code = 401, detail="Attendance taken already")
    if current_time < 12:
        attedance_form = models.Attendance(present=True, email=email, fullname=name, session="Morning")
    elif current_time > 12 and current_time < 19:
        attedance_form = models.Attendance(present=True, email=email, fullname=name, session="Afternoon")
    elif current_time > 19:
        attedance_form = models.Attendance(present=True, email=email, fullname=name, session="Evening")



    db.add(attedance_form)
    db.commit()
    db.refresh(attedance_form)
    return "Signed in successfully"

@app.get("/attendance", tags=["Attendance"])
async def get_attendance(db: Session =Depends(get_db)):
    date_today = date.today()

    return db.query(models.Attendance).filter(
        models.Attendance.created_at == date_today).all()[::-1]

@app.post("/attendance/date", tags=["Attendance"])
async def get_attendance_by_date(form: AttendanceByDate, db: Session =Depends(get_db)):
    date_today = date.today()
    if form.date <= date_today:
        return db.query(models.Attendance).filter(
            models.Attendance.created_at == form.date).all()[::-1]
    else:
        raise HTTPException(status_code=404, detail="No entry found in the database.")        


@app.get("/attendance/{email}", tags=["Attendance"])
async def get_attendance(email: EmailStr, db: Session =Depends(get_db)):
    
    if check_email := db.query(models.Users).filter(models.Users.email == email).first():
        return db.query(models.Attendance).filter(
            models.Attendance.email==email).limit(30).all()[::-1]
    else:
        raise HTTPException(status_code =404, detail="User with this email address not found")


if __name__=="__name__":
    uvicorn.run(app, host=8080)    
