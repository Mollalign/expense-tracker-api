from ninja import Schema

class UserRegisterSchema(Schema):
    full_name: str
    email: str
    password: str

class UserLoginSchema(Schema):
    email: str
    password: str  

class TokenSchema(Schema):
    access: str
    refresh: str      

class ForgotPasswordSchema(Schema):
    email: str  

class VerifyCodeSchema(Schema):
    email: str
    code: str
    new_password: str    