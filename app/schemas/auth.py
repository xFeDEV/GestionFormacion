from pydantic import BaseModel, EmailStr
from app.schemas.users import UserOut

class ResponseLoggin(BaseModel):
    user: UserOut
    access_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ValidateResetTokenRequest(BaseModel):
    token: str

class ValidateResetTokenResponse(BaseModel):
    valid: bool
    message: str

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "nueva_contraseña_segura123"
            }
        }

class ResetPasswordResponse(BaseModel):
    message: str
    success: bool
