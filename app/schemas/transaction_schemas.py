from locale import currency
from pydantic import BaseModel

class Deposit(BaseModel):
    account_number: int
    amount: int
    currency:str
    type: str

class DepositResponse(BaseModel):
    message:str

    class Config:
        from_attributes = True

class Withdrawal(Deposit):
    pass

class WithdrawalResponse(BaseModel):
    message: str

    class Config:
        from_attributes = True
        
    