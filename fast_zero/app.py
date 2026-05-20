from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from fast_zero.database import engine, get_db
from fast_zero.models import User, Account, Category, Transaction, mapeador
from fast_zero.schemas import *

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # depois você restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mapeador.metadata.create_all(bind=engine)
#users 
@app.post("/users/", status_code=201, response_model=Message)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = User(**user.model_dump())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "message": "Usuário criado com sucesso",

    }

@app.get("/users/", response_model=UserList)
def read_users(db: Session = Depends(get_db)):

    users = db.query(User).all()

    return {"users": users}

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    return user

@app.put("/users/{user_id}", response_model=Message)
def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    for key, value in user.model_dump().items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return {"message": "Usuario atualizado com sucesso"}


@app.patch("/users/{user_id}", response_model=Message)
def patch_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return {"message": "Usuario atualizado com sucesso"}


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")

    db.delete(db_user)
    db.commit()

    return {"message": "Usuario deletado"}

#login

@app.post("/login")
def login(data: dict, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data["email"]).first()

    if not user:
        raise HTTPException(status_code=401, detail="Email inválido")

    if user.password != data["password"]:
        raise HTTPException(status_code=401, detail="Senha inválida")

    return {
        "message": "Login realizado com sucesso",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email
        }
    }

#contas

@app.post("/accounts/", status_code=201, response_model=Message)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):

    user = db.get(User, account.user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    db_account = Account(**account.model_dump())

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    return {"message": "Conta criada com sucesso"}


@app.get("/accounts/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@app.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    return account

@app.get("/users/{user_id}/accounts", response_model=List[AccountResponse])
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):

    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .all()
    )

    return accounts

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    for key, value in user.model_dump().items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return {"message": "Conta atualizada com sucesso"}

@app.put("/accounts/{account_id}", response_model=Message)
def update_account(
    account_id: int,
    account: AccountCreate,
    db: Session = Depends(get_db)
):

    db_account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .first()
    )

    if not db_account:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada"
        )

    for key, value in account.model_dump().items():
        setattr(db_account, key, value)

    db.commit()
    db.refresh(db_account)

    return {"message": "Conta atualizada"}

@app.delete("/accounts/{account_id}", response_model=Message)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.id == account_id).first()

    if not db_account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    db.delete(db_account)
    db.commit()

    return {"message": "Conta deletada"}

#transações

@app.post("/transactions/", response_model=Message)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):

    # 1️⃣ Verifica se a conta existe
    account = db.query(Account).filter(Account.id == transaction.conta_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    user = db.get(User, transaction.user_id)
    categoria = db.get(Category, transaction.categoria_id)

    if not user:
        raise HTTPException(404, "Usuário não encontrado")

    if not categoria:
        raise HTTPException(404, "Categoria não encontrada")

    # 2️⃣ Aplica regra de saldo
    if transaction.tipo == "receita":
        account.saldo_inicial += transaction.valor

    elif transaction.tipo == "despesa":
        account.saldo_inicial -= transaction.valor

    else:
        raise HTTPException(status_code=400, detail="Tipo de transação inválido")

    db_transaction = Transaction(**transaction.model_dump())

    db.add(db_transaction)

    db.commit()
    db.refresh(db_transaction)

    return {"message": "Transação criada com sucesso"}

@app.get("/transactions/", response_model=List[TransactionResponse])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return transaction

@app.put("/transactions/{transaction_id}", response_model=Message)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    account = db.query(Account).filter(Account.id == transaction.conta_id).first()

    # 🔄 1️⃣ Reverte efeito antigo
    if transaction.tipo == "receita":
        account.saldo_inicial -= transaction.valor
    elif transaction.tipo == "despesa":
        account.saldo_inicial += transaction.valor

    # 🔄 2️⃣ Atualiza dados da transação
    update_data = transaction_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    # 🔄 3️⃣ Aplica novo efeito
    if transaction.tipo == "receita":
        account.saldo_inicial += transaction.valor
    elif transaction.tipo == "despesa":
        if account.saldo_inicial < transaction.valor:
            raise HTTPException(status_code=400, detail="Saldo insuficiente")
        account.saldo_inicial -= transaction.valor

    db.commit()
    db.refresh(transaction)

    return {"message": "Transação atualizada com sucesso"}

@app.delete("/transactions/{transaction_id}", response_model=Message)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):

    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    account = db.query(Account).filter(Account.id == transaction.conta_id).first()

    # 🔄 Reverte o efeito da transação
    if transaction.tipo == "receita":
        account.saldo_inicial -= transaction.valor
    elif transaction.tipo == "despesa":
        account.saldo_inicial += transaction.valor

    db.delete(transaction)
    db.commit()

    return {"message": "Transação deletada e saldo atualizado"}

#categoria

@app.post("/categories/", response_model=Message)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return {"message": "Categoria criada com sucesso"}


@app.get("/categories/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    return category

@app.get("/users/{user_id}/categories", response_model=List[CategoryResponse])
def get_user_categories(user_id: int, db: Session = Depends(get_db)):

    categories = (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .all()
    )

    return categories

@app.patch("/categories/{category_id}", response_model=Message)
def update_category_partial(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):

    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    for key, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return {"message": "Categoria atualizada"}


@app.delete("/categories/{category_id}", response_model=Message)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    db.delete(category)
    db.commit()

    return {"message": "Categoria deletada"}