# API de Pedidos com FastAPI

API REST para um sistema de pedidos (ex: pizzaria), com cadastro de usuário, login com JWT e controle de acesso — cada usuário só vê e altera os próprios pedidos, e o administrador vê todos.

## Tecnologias

- **FastAPI** + Uvicorn
- **SQLAlchemy** (SQLite) com migrações via **Alembic**
- **JWT** (python-jose) com access token e refresh token
- Senhas com hash **bcrypt** (passlib)
- Validação com **Pydantic**

## Endpoints

### Autenticação — `/auth`

| Método | Rota | O que faz |
|---|---|---|
| POST | `/auth/criar_conta` | Cadastra um usuário |
| POST | `/auth/login` | Login com e-mail e senha, devolve access + refresh token |
| POST | `/auth/login-form` | Login pelo formulário OAuth2 (usado no botão "Authorize" do `/docs`) |
| POST | `/auth/refresh` | Gera um novo access token |

### Pedidos — `/pedidos` (exige token)

| Método | Rota | O que faz |
|---|---|---|
| POST | `/pedidos/criar-pedido` | Cria um pedido |
| POST | `/pedidos/pedido/adicionar-item/{id_pedido}` | Adiciona item (sabor, tamanho, quantidade, preço) |
| POST | `/pedidos/pedido/remover-item/{id_item_pedido}` | Remove item e recalcula o total |
| POST | `/pedidos/pedido/finalizar/{id_pedido}` | Finaliza o pedido |
| POST | `/pedidos/pedido/cancelar/{id_pedido}` | Cancela o pedido |
| GET | `/pedidos/pedido/{id_pedido}` | Detalhes de um pedido |
| GET | `/pedidos/listar/pedidos-usuario` | Pedidos do usuário logado |
| GET | `/pedidos/pedido/listar` | Todos os pedidos (somente admin) |

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env        # e preencha uma SECRET_KEY própria
alembic upgrade head        # cria o banco bando.db
uvicorn main:app --reload
```

Documentação interativa em http://127.0.0.1:8000/docs
