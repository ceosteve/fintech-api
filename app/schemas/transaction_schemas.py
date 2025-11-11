
from typing import Dict
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

class Transer(BaseModel):
    sender_wallet_account_number: int
    receiver_wallet_account_number: int
    amount: int
    type: str
    currency: str

class TransferOut(BaseModel):
    message:Dict = {}


    