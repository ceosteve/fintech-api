

from fastapi import Depends, HTTPException, status, APIRouter
from app import dependencies
from app.database.database import get_db
from app.dependencies import get_current_user
from app.schemas import transaction_schemas
from sqlalchemy.orm import Session
from app.database import models
import logging


logger = logging.getLogger("fintech")


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


"""deposit endpoint"""
@router.post("/deposit", status_code=status.HTTP_200_OK, response_model=transaction_schemas.DepositResponse)
def deposit_to_wallet(deposit_info:transaction_schemas.Deposit, db:Session=Depends(get_db),
                      current_user:str=Depends(get_current_user)):
    
    existing_account = db.query(models.Wallets).filter(models.Wallets.user_id==current_user.id, 
                                                      models.Wallets.account_number==deposit_info.account_number).first()

    if not existing_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"account number: {deposit_info.account_number} does not exist!")
    
    logger.warning("user tried to access a non existing account")
    
    if existing_account.currency != deposit_info.currency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You cannot deposit to an account with non-matching currency!")
    
    logger.error("user tried depositing to a non-matching currency account")
    
    if existing_account.is_active =="False":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="You cannot transact with an inactive account!")
    
    logging.error("user tried transacting in an inactive account")
    
    existing_account.balance += deposit_info.amount

    new_transaction= models.Transactions(
        sender_wallet_account_number = deposit_info.account_number,
        receiver_wallet_account_number = deposit_info.account_number,
        amount = deposit_info.amount,
        type = deposit_info.type,
        currency = deposit_info.currency,
        status = "completed"
    )
    db.add(new_transaction)
    db.flush()

    logger.info(f"new transaction with id {new_transaction.id} was created")

    new_ledger_entry = models.LedgerEntries(
        transaction_id = new_transaction.id,
        wallet_id = existing_account.id,
        entry_type = models.EntryType.credit,
        amount = deposit_info.amount,
        balance_after =existing_account.balance,
        currency = deposit_info.currency,
        narration = "cash deposit"
    )
    
    db.add(new_ledger_entry)

    logger.info(f"new ledger entry  with id {new_ledger_entry.id} was created")

    db.commit()
    db.refresh(new_transaction)
    db.refresh(new_ledger_entry)

    return {"message":f"You have successfully deposited {deposit_info.currency}:{deposit_info.amount},new balance is {deposit_info.currency}:{existing_account.balance}"}


"""withdrawal endpoint """
@router.post("/withdraw", status_code=status.HTTP_200_OK, response_model=transaction_schemas.WithdrawalResponse)
def withdraw_from_wallet(withdrawal_info:transaction_schemas.Withdrawal, 
                          db:Session=Depends(get_db), current_user:str=Depends(get_current_user)):
    
    existing_account = db.query(models.Wallets).filter(models.Wallets.user_id==current_user.id,
                                                      models.Wallets.account_number==withdrawal_info.account_number).first()
    
    if not existing_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f" account number: {withdrawal_info.account_number} does not exist!")
    
    logging.warning("user tried withdrawing from a non existing account")
    
    if existing_account.balance < withdrawal_info.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    
    logging.warning("user tried withdrawing morr than the account balance")
    
    if existing_account.currency != withdrawal_info.currency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You cannot withdraw from an account with non-matching currency!")
    
    logger.error("user tried withdrawing from a non-matching currency account")
    
    if existing_account.is_active =="False":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="You cannot transact with an inactive account!")
    
    logging.error("user tried transacting in an inactive account")

    existing_account.balance -=withdrawal_info.amount

    new_transaction= models.Transactions(
        sender_wallet_account_number = withdrawal_info.account_number,
        receiver_wallet_account_number = withdrawal_info.account_number,
        amount = withdrawal_info.amount,
        type = withdrawal_info.type,
        currency = withdrawal_info.currency,
        status = "completed"
)
    db.add(new_transaction)
    db.flush()

    logger.info(f"new transaction with id {new_transaction.id} was created")

    new_ledger_entry = models.LedgerEntries(
        transaction_id = new_transaction.id,
        wallet_id = existing_account.id,
        entry_type = models.EntryType.debit,
        amount = withdrawal_info.amount,
        balance_after =existing_account.balance,
        currency = withdrawal_info.currency,
        narration = "cash withdrawal"
    )

    db.add(new_ledger_entry)

    logger.info(f"new ledger entry  with id {new_ledger_entry.id} was created")

    db.commit()
    db.refresh(new_transaction)
    db.refresh(new_ledger_entry)


    return {"message":f"You have successfully withdrawn {withdrawal_info.currency}:{withdrawal_info.amount}, new balance is {withdrawal_info.currency}:{existing_account.balance}"}



"""money transfer endpoint"""

@router.post("/transfer", status_code=status.HTTP_200_OK, response_model=transaction_schemas.TransferOut)
def transfer_to_wallet(transfer_info:transaction_schemas.Transer, db:Session=Depends(get_db),
                        current_user:str=Depends(get_current_user)):
    
    existing_wallet = db.query(models.Wallets).filter(
        models.Wallets.user_id==current_user.id).first()
    
    if not existing_wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="user has no digital wallet!")
    
    logging.error("user tried transactions with a non existing wallet")
    
    """query for sender and receiver account numbers"""

    accounts = db.query(models.Wallets).filter(models.Wallets.account_number.in_([
        transfer_info.sender_wallet_account_number,
        transfer_info.receiver_wallet_account_number
    ])).all()


    if len(accounts) !=2:
        missing = {
            transfer_info.sender_wallet_account_number,
            transfer_info.receiver_wallet_account_number
        } - {a.account_number for a in accounts}

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"wallet(s) not found for account(s):{','.join(map(str, missing))}")
    
    sender_existing_account = next(a for a in accounts if a.account_number==transfer_info.sender_wallet_account_number)
    receiver_existing_account = next(a for a in accounts if a.account_number==transfer_info.receiver_wallet_account_number)

    
    if  sender_existing_account.is_active== False or receiver_existing_account.is_active == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail="You cannot transact with an inactive account!")
    
    logger.warning("user tried transacting with an inactive account")
    
    if sender_existing_account.currency != transfer_info.currency or receiver_existing_account.currency != transfer_info.currency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You cannot transact with non-matching currencies!")
    
    logger.error("user tried transacting with non-matching currency accounts")

    if sender_existing_account.balance < transfer_info.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")
    
    logger.error("user tried transfering an amount greater than the account balance")
    
    sender_existing_account.balance -= transfer_info.amount
    receiver_existing_account.balance += transfer_info.amount

    new_transaction = models.Transactions(
        sender_wallet_account_number = transfer_info.sender_wallet_account_number,
        receiver_wallet_account_number = transfer_info.receiver_wallet_account_number,
        type = transfer_info.type,
        amount = transfer_info.amount,
        currency = transfer_info.currency,
        status = "completed"
    )

    db.add(new_transaction)
    db.flush()

    new_debit_ledger = models.LedgerEntries(
        transaction_id = new_transaction.id,
        wallet_id = sender_existing_account.id,
        entry_type = models.EntryType.debit,
        amount = transfer_info.amount,
        balance_after =sender_existing_account.balance,
        currency = transfer_info.currency,
        narration = "cash transfer"
    )

    db.add(new_debit_ledger)

    logger.info(f"new  debit ledger entry  with id {new_debit_ledger.id} was created")

    new_credit_ledger = models.LedgerEntries(
        transaction_id = new_transaction.id,
        wallet_id = receiver_existing_account.id,
        entry_type = models.EntryType.credit,
        amount = transfer_info.amount,
        balance_after =receiver_existing_account.balance,
        currency = transfer_info.currency,
        narration = "cash received "
    )

    db.add(new_credit_ledger)

    logger.info(f"new credit ledger with id {new_credit_ledger.id} was creaeted ")

    db.commit()
    db.refresh(new_transaction)
    db.refresh(new_credit_ledger)
    db.refresh(new_debit_ledger)

    return {"message":{
        "sender_reference":f"{new_transaction.sender_ref}",
        "receiver_refrence":f"{new_transaction.receiver_ref}",
        "transfer_amount":f"{transfer_info.amount}",
        "sender_balance":f"{sender_existing_account.balance}"
    }}
