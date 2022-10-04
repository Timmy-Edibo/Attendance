from pydantic import BaseModel
from datetime import date


class AttendanceForm(BaseModel):
    user: str
    dept: str
    session: str
    qrcode: str

    class Config:
        schema_extra = {
            "example": {
                "user": "Admin",
                "dept": "Admin Department",
                "session": "Afternoon",
                "qrcode": "enter your qrcode here!!!"
            }
        }



class RegisterForm(BaseModel):
    qrcode: str
    # session: str

    # attendance_table: str


class AttendanceForm(BaseModel):
    qrcode: str
    # is_present: bool

    # user_table


class AttendanceByDate(BaseModel):
    date: date    