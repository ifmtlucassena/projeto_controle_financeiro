from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
from decimal import Decimal


class Transacao(ABC):
    def __init__(
        self,
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str
    ) -> None:
        self._valor = valor
        self._data = data
        self._descricao = descricao
        self._categoria = categoria

    @property
    def valor(self) -> Decimal:
        return self._valor

    @property
    def data(self) -> datetime:
        return self._data

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def categoria(self) -> str:
        return self._categoria

    @abstractmethod
    def para_dicionario(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def obter_tipo(self) -> str:
        pass


class Receita(Transacao):
    def __init__(
        self,
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str,
        conta_destino: str
    ) -> None:
        super().__init__(valor, data, descricao, categoria)
        self._conta_destino = conta_destino

    @property
    def conta_destino(self) -> str:
        return self._conta_destino

    def para_dicionario(self) -> Dict[str, Any]:
        return {
            'tipo': self.obter_tipo(),
            'valor': float(self.valor),
            'data': self.data.isoformat(),
            'descricao': self.descricao,
            'categoria': self.categoria,
            'conta_destino': self.conta_destino
        }

    def obter_tipo(self) -> str:
        return 'receita'


class Despesa(Transacao):
    def __init__(
        self,
        valor: Decimal,
        data: datetime,
        descricao: str,
        categoria: str,
        metodo_pagamento: str,
        estabelecimento: str
    ) -> None:
        super().__init__(valor, data, descricao, categoria)
        self._metodo_pagamento = metodo_pagamento
        self._estabelecimento = estabelecimento

    @property
    def metodo_pagamento(self) -> str:
        return self._metodo_pagamento

    @property
    def estabelecimento(self) -> str:
        return self._estabelecimento

    def para_dicionario(self) -> Dict[str, Any]:
        return {
            'tipo': self.obter_tipo(),
            'valor': float(self.valor),
            'data': self.data.isoformat(),
            'descricao': self.descricao,
            'categoria': self.categoria,
            'metodo_pagamento': self.metodo_pagamento,
            'estabelecimento': self.estabelecimento
        }

    def obter_tipo(self) -> str:
        return 'despesa'
