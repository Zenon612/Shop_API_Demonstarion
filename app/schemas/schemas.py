from datetime import datetime
from typing import List
import re

from pydantic import BaseModel, Field, EmailStr, field_validator


class RoleRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    role_ids: List[int] = Field(default=[1])
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Требования к паролю: минимум 8 символов, буквы, цифры, спецсимволы"""
        if len(v) < 8:
            raise ValueError('Пароль должен быть минимум 8 символов')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать заглавные буквы (A-Z)')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать строчные буквы (a-z)')
        
        if not re.search(r'[0-9]', v):
            raise ValueError('Пароль должен содержать цифры (0-9)')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\[\]\\\/\-_=+]', v):
            raise ValueError('Пароль должен содержать спецсимволы (!@#$%^&* и т.д.)')
        
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Username: только буквы, цифры, подчеркивания, дефисы"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username может содержать только буквы, цифры, подчеркивания и дефисы')
        return v.strip()


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[RoleRead] = []
    model_config = {"from_attributes": True}


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Наименование товара")
    price: float = Field(..., gt=0, description="Цена (должна быть больше 0)")
    description: str | None = Field(None, max_length=1000, description="Описание")


class ItemUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    description: str | None = Field(None, max_length=1000)


class ItemPartialUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    price: float | None = Field(None, gt=0)
    description: str | None = Field(None, max_length=1000)


class ItemResponse(ItemCreate):
    id: int = Field(..., description="Идентификатор")

    model_config = {"from_attributes": True}
