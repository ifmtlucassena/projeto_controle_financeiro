from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.transacao import Transacao, Receita, Despesa


class TransacaoFactory:
    @staticmethod
    def criar_transacao(
        tipo: str,
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str,
        **kwargs
    ) -> Transacao:
        tipo = tipo.lower().strip()

        if tipo == 'receita':
            return TransacaoFactory._criar_receita(
                valor, data, descricao, categoria, **kwargs
            )
        elif tipo == 'despesa':
            return TransacaoFactory._criar_despesa(
                valor, data, descricao, categoria, **kwargs
            )
        else:
            raise ValueError(
                f"Tipo de transação inválido: '{tipo}'. "
                "Tipos válidos: 'receita' ou 'despesa'"
            )

    @staticmethod
    def _criar_receita(
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str,
        **kwargs
    ) -> Receita:
        conta_destino: Optional[str] = kwargs.get('conta_destino')

        if not conta_destino:
            raise ValueError(
                "Para criar uma receita, o campo 'conta_destino' é obrigatório"
            )

        return Receita(
            valor=valor,
            data=data,
            descricao=descricao,
            categoria=categoria,
            conta_destino=conta_destino
        )

    @staticmethod
    def _criar_despesa(
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str,
        **kwargs
    ) -> Despesa:
        metodo_pagamento: Optional[str] = kwargs.get('metodo_pagamento')
        estabelecimento: Optional[str] = kwargs.get('estabelecimento')

        if not metodo_pagamento:
            raise ValueError(
                "Para criar uma despesa, o campo 'metodo_pagamento' é obrigatório"
            )

        if not estabelecimento:
            raise ValueError(
                "Para criar uma despesa, o campo 'estabelecimento' é obrigatório"
            )

        return Despesa(
            valor=valor,
            data=data,
            descricao=descricao,
            categoria=categoria,
            metodo_pagamento=metodo_pagamento,
            estabelecimento=estabelecimento
        )
