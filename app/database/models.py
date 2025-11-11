import random
import shortuuid
import enum
import uuid
from app.database.database import Base
from sqlalchemy import Column, String, Date, VARCHAR, Enum, Boolean, TIMESTAMP, ForeignKey, Numeric, text, Integer, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class UserRole(str, enum.Enum):
    admin = "admin"
    customer = "customer"

class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"


class Status(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class EntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"

class Gender(str, enum.Enum):
    Male = "Male"
    Female = "Female"


class Users(Base):
    __tablename__ = "users"

    id = Column (UUID(as_uuid=True),primary_key= True,
                 default=uuid.uuid4, unique=True, nullable=False)
    public_id = Column(String(8), unique=True, nullable=False, default=lambda: shortuuid.uuid()[:8])
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birthday = Column(Date, nullable=False)
    email = Column (VARCHAR, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), server_default=UserRole.customer, nullable=False)
    is_active = Column(Boolean, server_default=text("True"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    wallets = relationship("Wallets", back_populates="user")
    tokens=relationship("RefreshTokens", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

class Wallets(Base):
    __tablename__ = "wallets"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_number= Column (Integer, default=lambda:random.randint(100000000,999999999), unique=True, nullable=False)
    balance = Column(Numeric(18,2), nullable=True, server_default=text("0.00"))
    currency = Column(VARCHAR(3), nullable=False)
    is_active = Column (Boolean, server_default=text("False"), nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    user = relationship("Users", back_populates="wallets")
    outgoing_transactions = relationship("Transactions", back_populates="sender_wallet", foreign_keys="[Transactions.sender_wallet_account_number]", cascade="all, delete")
    incoming_transactions = relationship("Transactions", back_populates="receiver_wallet", foreign_keys="[Transactions.receiver_wallet_account_number]", cascade="all, delete")


class Transactions(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=True)
    reference = Column(String(10), default = shortuuid.ShortUUID(alphabet="ABCDEFGHIJKLMNOPQRDTUVWXYZ").random(length=10),
                        unique=True, nullable=False)
    sender_ref = Column(String(10), default = shortuuid.ShortUUID(alphabet="ABCDEFGHIJKLMNOPQRDTUVWXYZ").random(length=10), 
                        unique=True, nullable=False)
    receiver_ref = Column(String(10), default = shortuuid.ShortUUID(alphabet="ABCDEFGHIJKLMNOPQRDTUVWXYZ").random(length=10), 
                          unique=True, nullable=False)

    sender_wallet_account_number = Column(BigInteger, ForeignKey("wallets.account_number"), nullable=False)
    receiver_wallet_account_number = Column(BigInteger, ForeignKey("wallets.account_number"), nullable=False)
  
    amount = Column(Numeric(18,2), nullable=False)
    currency= Column(String(3), nullable=False, server_default="KES")
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(Status), default=Status.pending, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    sender_wallet = relationship("Wallets", back_populates="outgoing_transactions", foreign_keys=[sender_wallet_account_number])
    receiver_wallet = relationship("Wallets", back_populates="incoming_transactions", foreign_keys=[receiver_wallet_account_number])

    ledger_entries = relationship("LedgerEntries", back_populates="transaction")


class LedgerEntries(Base):
    __tablename__ = "ledger_entries"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False, index=True)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    entry_type = Column(Enum(EntryType), nullable=False)
    amount = Column(Numeric(18,2), nullable=False)
    currency = Column(String(3), nullable=False)
    narration = Column(String(200), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    transaction = relationship("Transactions", back_populates="ledger_entries")

class RefreshTokens(Base):
    __tablename__="refresh_tokens"
    id= Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at= Column(DateTime, nullable=False)
    hashed_token=Column(String, nullable=False)

    user=relationship("Users",back_populates="tokens")
