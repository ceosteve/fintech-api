from locale import currency
from pydantic import BaseModel

class WalletCreate(BaseModel):
    currency: str
    initial_deposit : int


class WalletsOut(BaseModel):
    public_id:str
    balance: int
    currency: str
    account_number: int
    is_active: bool

    class Config:
        from_attributes= True

class WalletsFreeze(BaseModel):
    is_active:bool

