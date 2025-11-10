from locale import currency
from pydantic import BaseModel

class WalletCreate(BaseModel):
    currency: str
    initial_deposit : int


class WalletsOut(BaseModel):
    balance: int
    currency: str
    account_number: int

    class Config:
        from_attributes= True

