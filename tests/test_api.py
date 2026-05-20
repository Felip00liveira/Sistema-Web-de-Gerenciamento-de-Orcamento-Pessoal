
def create_user_helper(client):
    res = client.post(
        "/users/",
        json={
            "nome": "user",
            "email": "user@test.com",
            "password": "123",
            "telefone": "+5511999999999",
            "cpf": "12345678901",
            "data_nascimento": "2000-01-01"
        }
    )
    return res


def test_create_user(client):
    response = create_user_helper(client)

    assert response.status_code == 201
    assert response.json()["message"] == "Usuário criado com sucesso"


def test_get_users(client):
    create_user_helper(client)

    response = client.get("/users/")

    assert response.status_code == 200
    assert len(response.json()["users"]) >= 1


def test_get_user_by_id(client):
    create_user_helper(client)

    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["nome"] == "user"


def test_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404


def test_update_user(client):
    create_user_helper(client)

    response = client.put(
        "/users/1",
        json={
            "nome": "novo",
            "email": "novo@test.com",
            "password": "123",
            "telefone": "+5511999999998",
            "cpf": "12345678902",
            "data_nascimento": "2000-01-01"
        }
    )

    
    assert response.status_code == 200


def test_delete_user(client):
    create_user_helper(client)

    response = client.delete("/users/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Usuario deletado"



def create_account_helper(client):
    create_user_helper(client)

    res = client.post(
        "/accounts/",
        json={
            "nome_conta": "Conta",
            "banco": "Nubank",
            "tipo_conta": "corrente",
            "saldo_inicial": 100.0,
            "user_id": 1
        }
    )
    return res


def test_create_account(client):
    response = create_account_helper(client)

    assert response.status_code == 201
    assert response.json()["message"] == "Conta criada com sucesso"


def test_list_accounts(client):
    response = client.get("/accounts/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_account_not_found(client):
    response = client.get("/accounts/999")
    assert response.status_code == 404


def test_delete_account(client):
    create_account_helper(client)

    response = client.delete("/accounts/1")

    assert response.status_code == 200


def create_category_helper(client):
    create_user_helper(client)

    res = client.post(
        "/categories/",
        json={
            "nome": "Categoria",
            "tipo": "despesa",
            "user_id": 1
        }
    )
    return res


def test_create_category(client):
    response = create_category_helper(client)

    assert response.status_code == 200
    assert response.json()["message"] == "Categoria criada com sucesso"


def test_list_categories(client):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_category_not_found(client):
    response = client.get("/categories/999")
    assert response.status_code == 404


def test_delete_category(client):
    create_category_helper(client)

    response = client.delete("/categories/1")

    assert response.status_code == 200



def create_full_setup(client):
    create_user_helper(client)

    client.post(
        "/accounts/",
        json={
            "nome_conta": "Conta",
            "banco": "Nubank",
            "tipo_conta": "corrente",
            "saldo_inicial": 100.0,
            "user_id": 1
        }
    )

    client.post(
        "/categories/",
        json={
            "nome": "Geral",
            "tipo": "despesa",
            "user_id": 1
        }
    )

    return 1, 1  


def test_create_transaction_receita(client):
    account_id, category_id = create_full_setup(client)

    response = client.post(
        "/transactions/",
        json={
            "descricao": "Salario",
            "valor": 50.0,
            "tipo": "receita",
            "data": "2024-01-01",
            "user_id": 1,
            "conta_id": account_id,
            "categoria_id": category_id
        }
    )

    assert response.status_code == 200


def test_create_transaction_despesa(client):
    account_id, category_id = create_full_setup(client)

    response = client.post(
        "/transactions/",
        json={
            "descricao": "Compra",
            "valor": 30.0,
            "tipo": "despesa",
            "data": "2024-01-01",
            "user_id": 1,
            "conta_id": account_id,
            "categoria_id": category_id
        }
    )

    assert response.status_code == 200


def test_transaction_conta_inexistente(client):
    create_user_helper(client)

    response = client.post(
        "/transactions/",
        json={
            "descricao": "Erro",
            "valor": 10.0,
            "tipo": "receita",
            "data": "2024-01-01",
            "user_id": 1,
            "conta_id": 999,
            "categoria_id": 1
        }
    )

    assert response.status_code == 404


def test_transaction_tipo_invalido(client):
    account_id, category_id = create_full_setup(client)

    response = client.post(
        "/transactions/",
        json={
            "descricao": "Erro",
            "valor": 10.0,
            "tipo": "invalido",
            "data": "2024-01-01",
            "user_id": 1,
            "conta_id": account_id,
            "categoria_id": category_id
        }
    )

    assert response.status_code == 400