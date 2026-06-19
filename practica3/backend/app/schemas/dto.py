from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: str = Field(min_length=5, max_length=160)
    full_name: str = Field(default="", max_length=160)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class ProviderIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    nit: str = Field(min_length=2, max_length=40)
    email: str = ""
    phone: str = ""
    address: str = ""
    category: str = "General"
    is_active: bool = True


class ProviderOut(ProviderIn):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    issue_date: date | None
    provider_name: str
    provider_nit: str
    subtotal: float
    taxes: float
    total: float
    status: str
    file_name: str
    raw_text: str
    validation_errors: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogOut(BaseModel):
    id: int
    created_at: datetime
    username: str
    document_name: str
    status: str
    result: str
    invoice_id: int | None

    model_config = ConfigDict(from_attributes=True)


class EmailReportRequest(BaseModel):
    recipient: str = Field(min_length=5, max_length=160)
    report_type: str = Field(default="pdf", pattern="^(pdf|csv)$")
