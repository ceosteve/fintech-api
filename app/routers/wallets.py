
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.dependencies import get_current_user, require_admin
from app.schemas import wallet_schemas
from app.database import models
from migrations.versions import db8468efba1a_alter_is_active_column_of_wallets_table
import logging 

logger = logging.getLogger("fintech")


router= APIRouter(
    prefix="/wallets",
    tags = ["User digital wallets"]
)

"""endpoint to create a wallet"""
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
                             detail="initial deposit is below minimum deposit")
    
    new_wallet = models.Wallets(
    user_id=current_user.id,
    balance=wallet_data.initial_deposit,
    currency=wallet_data.currency,
    is_active=True)

    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    logger.info(f"user created new wallet with id {new_wallet.public_id}")
    return new_wallet



"""endpoint to retrieve wallet from database"""
@router.get("/retrieve/{id}", status_code=status.HTTP_200_OK, response_model=wallet_schemas.WalletsOut)
def retrieve_wallet(id:str, db:Session=Depends(get_db), current_user:str=Depends(get_current_user)):

    wallet = db.query(models.Wallets).filter(models.Wallets.public_id==id).first()

    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    
    if current_user.id != wallet.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no permission to perform this operation")
    
    return wallet
   


""""endpoint to delete a wallet"""
@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(id:str, db:Session=Depends(get_db), current_user:models.Users=Depends(require_admin)):
    
    wallet = db.query(models.Wallets).filter(models.Wallets.public_id==id).first()

    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"wallets with id: {id} not found")
    
    if current_user.role == models.UserRole.admin:
        db.delete(wallet)
        db.commit()
    
        logger.info(f"user deleted wallet with id {wallet.public_id}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this operation")
    
    return {"message":f"wallet: {wallet.public_id} has successfully been deleted"}


"""freeze/deactivate wallet"""
@router.put("/freeze/{id}", status_code=status.HTTP_200_OK, response_model=wallet_schemas.WalletsOut)
def freeze_wallet(id:str, status_update: wallet_schemas.WalletsFreeze, db:Session=Depends(get_db), current_user:models.Users=Depends(require_admin)):
    
    query = db.query(models.Wallets).filter(models.Wallets.public_id==id)
    wallet = query.first()

    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet with id {id} not found")
    
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this operation")
    
    data = status_update.dict()

    query.update(data, synchronize_session=False)

    logger.info(f"user deactivated wallet with id number {wallet.public_id}")
    db.commit()
    
    return query.first()



"""activate wallet"""
@router.put("/activate/{id}", status_code=status.HTTP_200_OK, response_model=wallet_schemas.WalletsOut)
def activate_wallet(id:str, status_update: wallet_schemas.WalletsFreeze, db:Session=Depends(get_db), current_user:models.Users=Depends(require_admin)):
    
    query = db.query(models.Wallets).filter(models.Wallets.public_id==id)
    wallet = query.first()

    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet with id {id} not found")
    
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot perform this operation")
    
    logger.error("unauthorized user tried activating a wallet")
    
    data = status_update.dict()

    query.update(data, synchronize_session=False)
    db.commit()
    
    return query.first()

    