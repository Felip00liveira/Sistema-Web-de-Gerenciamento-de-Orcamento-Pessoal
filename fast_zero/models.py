from datetime import datetime, date
from decimal import Decimal
from typing import List

from sqlalchemy import String, Numeric, ForeignKey, Date, func
from sqlalchemy.orm import Mapped, mapped_as_dataclass, mapped_column, registry, relationship

mapeador = registry()


@mapped_as_dataclass(mapeador)
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str]
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    telefone: Mapped[str] = mapped_column(unique=True)
    cpf: Mapped[str] = mapped_column(unique=True)
    data_nascimento: Mapped[date]

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    contas: Mapped[List["Account"]] = relationship(init=False, back_populates="user")
    categorias: Mapped[List["Category"]] = relationship(init=False, back_populates="user")
    transacoes: Mapped[List["Transaction"]] = relationship(init=False, back_populates="user")


@mapped_as_dataclass(mapeador)
class Account:
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome_conta: Mapped[str] = mapped_column(String(100))
    banco: Mapped[str] = mapped_column(String(100))
    tipo_conta: Mapped[str] = mapped_column(String(50))
    saldo_inicial: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)

    user: Mapped["User"] = relationship(init=False ,back_populates="contas")
    transacoes: Mapped[List["Transaction"]] = relationship(init=False, back_populates="conta")



@mapped_as_dataclass(mapeador)
class Category:
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(20))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(init=False, back_populates="categorias")
    transacoes: Mapped[List["Transaction"]] = relationship(init=False, back_populates="categoria")


@mapped_as_dataclass(mapeador)
class Transaction:
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(255))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    data: Mapped[date] = mapped_column(Date)
    tipo: Mapped[str] = mapped_column(String(20))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    conta_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    user: Mapped["User"] = relationship(init=False, back_populates="transacoes")
    conta: Mapped["Account"] = relationship(init=False, back_populates="transacoes")
    categoria: Mapped["Category"] = relationship(init=False, back_populates="transacoes")