
from locale import currency
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.dependencies import get_current_user
from app.schemas import wallet_schemas
from app.database import models

router= APIRouter(
    prefix="/wallets",
    tags = ["User digital wallets"]
)

@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=wallet_schemas.WalletsOut)
def create_wallet(wallet_data:wallet_schemas.WalletCreate, db:Session=Depends(get_db), current_user:str=Depends(get_current_user)):
   
    minimum_deposit = 500.00

    existing_wallet = db.query(models.Wallets).filter(models.Wallets.user_id==current_user.id, 
                                                      models.Wallets.currency==wallet_data.currency).first()
    
    if existing_wallet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="User already has a wallet with that currency")
    
    if wallet_data.initial_deposit < minimum_deposit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="initial is deposit below minimum deposit")
    
    new_wallet = models.Wallets(
    user_id=current_user.id,
    balance=wallet_data.initial_deposit,
    currency=wallet_data.currency,
    is_active=True)

    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    return new_wallet
    

    
