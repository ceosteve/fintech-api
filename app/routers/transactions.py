
from fastapi import Depends, HTTPException, status, APIRouter
from app.database.database import get_db
from app.dependencies import get_current_user
from app.schemas import transaction_schemas
from sqlalchemy.orm import Session
from app.database import models

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/deposit", status_code=status.HTTP_200_OK, response_model=transaction_schemas.DepositResponse)
def deposit_to_wallet(deposit_info:transaction_schemas.Deposit, db:Session=Depends(get_db),
                      current_user:str=Depends(get_current_user)):
    
    existing_wallet = db.query(models.Wallets).filter(models.Wallets.user_id==current_user.id).first()
    if not existing_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user has no digital wallet!")
    
    existing_account= db.query(models.Wallets).filter(models.Wallets.account_number==deposit_info.account_number).first()

    if not existing_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{deposit_info.account_number} does not exist!")
    
    existing_account.balance += deposit_info.amount

    new_transaction= models.Transactions(
        sender_wallet_account_number = deposit_info.account_number,
        receiver_wallet_account_number = deposit_info.account_number,
        amount = deposit_info.amount,
        type = deposit_info.type,
        status = "completed"
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {"message":f"You have successfully deposited {deposit_info.currency} {deposit_info.amount},new balance is {deposit_info.currency}:{existing_account.balance}"}



@router.post("/withdraw", status_code=status.HTTP_200_OK, response_model=transaction_schemas.WithdrawalResponse)
def withdraw_from_account(withdrawal_info:transaction_schemas.Withdrawal, 
                          db:Session=Depends(get_db), current_user:str=Depends(get_current_user)):
    
    existing_wallet = db.query(models.Wallets).filter(models.Wallets.user_id==current_user.id).first()
    if not existing_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user has no digital wallet!")
    
    existing_account= db.query(models.Wallets).filter(models.Wallets.account_number==withdrawal_info.account_number).first()

    if not existing_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{withdrawal_info.account_number} does not exist!")
    
    if existing_account.balance < withdrawal_info.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    
    existing_account.balance -=withdrawal_info.amount
    new_transaction= models.Transactions(
    sender_wallet_account_number = withdrawal_info.account_number,
    receiver_wallet_account_number = withdrawal_info.account_number,
    amount = withdrawal_info.amount,
    type = withdrawal_info.type,
    status = "completed"
)

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)


    return {"message":f"You have successfully withdrawn {withdrawal_info.currency}:{withdrawal_info.amount}, new balance is {withdrawal_info.currency}:{existing_account.balance}"}
