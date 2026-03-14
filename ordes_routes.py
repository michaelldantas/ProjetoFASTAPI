from fastapi import APIRouter, Depends, HTTPException
from models import Pedido, Usuario, ItemPedido
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from sqlalchemy.orm import Session
from dependecies import pegar_sessao,verificar_token
from typing import List

ordes_routes = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@ordes_routes.get("/")
async def pedidos():
    return {"mensagem": "Você acessou a rota de pedidos."}


@ordes_routes.post("/criar-pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido cadastrado com sucesso: {novo_pedido.id}"}


@ordes_routes.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:  
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    
    pedido.status = "CANCELADO"
    session.commit()
    return {
        "mensagem": f"Pedido número {pedido.id} cancelado com sucesso",
        "pedido": pedido
        }


@ordes_routes.get("/pedido/listar")
async def listar_pedido(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    else:
        pedidos = session.query(Pedido).all()
        return {
            "pedidos": pedidos
            }


@ordes_routes.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token) ):
    
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não existente.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    
    item_pedido = ItemPedido(item_pedido_schema.quantidade, item_pedido_schema.sabor, item_pedido_schema.tamanho,
                             item_pedido_schema.preco_unitario, id_pedido)
    
    session.add(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
            "mensagem": "Item do Pedido adicionado com sucesso.",
            "item_id": item_pedido.id,
            "preco_pedido": pedido.preco
            }


@ordes_routes.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token) ):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=400, detail="Item do Pedido não existente.")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {
            "mensagem": "Item do Pedido removido com sucesso.",
            "quantidade_itens_pedido": len(pedido.itens),
            "pedido": pedido
            }


@ordes_routes.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:  
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    
    pedido.status = "FINALIZADO"
    session.commit()
    return {
        "mensagem": f"Pedido número {pedido.id} finalizado com sucesso",
        "pedido": pedido
        }


@ordes_routes.get("/pedido/{id_pedido}")
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado.")
    if not usuario.admin and usuario.id != pedido.usuario:  
        raise HTTPException(status_code=401, detail="Você não tem autorização para realizar essa tarefa.")
    
    return {
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido
        }


@ordes_routes.get("/listar/pedidos-usuario", response_model=list[ResponsePedidoSchema])
async def listar_pedidos_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos