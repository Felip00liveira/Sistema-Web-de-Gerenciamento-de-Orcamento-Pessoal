from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

# -------- USER --------
class UserBase(BaseModel):
    nome: str
    password: str
    email: EmailStr
    telefone: str = Field(pattern=r"^\+\d{10,15}$")
    cpf: str = Field(pattern=r"^\d{11}$")
    data_nascimento: date

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nome: str
    password: str
    email: EmailStr
    telefone: str = Field(pattern=r"^\+\d{10,15}$")
    cpf: str = Field(pattern=r"^\d{11}$")
    data_nascimento: date

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserList(BaseModel):
    users: List[UserResponse]

# -------- MESSAGE --------
class Message(BaseModel):
    message: str

# -------- ACCOUNT --------
class AccountBase(BaseModel):
    nome_conta: str
    banco: str
    tipo_conta: str
    saldo_inicial: Decimal
    user_id: int

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: int

    class Config:
        from_attributes = True

# -------- TRANSACTION --------
class TransactionBase(BaseModel):
    descricao: str
    valor: Decimal
    data: date
    tipo: str
    user_id: int
    conta_id: int
    categoria_id: int

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    ddescricao: Optional[str] = None
    valor: Optional[Decimal] = None
    tipo: Optional[str] = None
    data: Optional[date] = None
    categoria_id: Optional[int] = None
    conta_id: Optional[int] = None

class TransactionResponse(TransactionBase):
    id: int

    class Config:
        from_attributes = True

# -------- CATEGORY --------
class CategoryBase(BaseModel):
    nome: str
    tipo: str
    user_id: int
class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    user_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True