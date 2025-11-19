from google.cloud.firestore import FieldFilter
import firebase_admin
from firebase_admin import credentials, firestore
from threading import Lock
from typing import List, Dict, Any, Optional
from decimal import Decimal
import os

class BancoDeDados:
    _instancia: Optional['BancoDeDados'] = None
    _lock: Lock = Lock()

    def __new__(cls) -> 'BancoDeDados':
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        if not firebase_admin._apps:
            cred_path = os.path.join(os.getcwd(), 'serviceAccountKey.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                pass
        self.db = firestore.client()

    def salvar_transacao(self, user_id: str, transacao: Dict[str, Any]) -> None:
        transacao_fs = transacao.copy()
        
        # Converter Decimal para float
        if 'valor' in transacao_fs and isinstance(transacao_fs['valor'], Decimal):
             transacao_fs['valor'] = float(transacao_fs['valor'])
        
        # Adicionar user_id para isolamento na coleção raiz
        transacao_fs['user_id'] = user_id
        
        # Salvar na coleção raiz 'transacoes'
        self.db.collection('transacoes').add(transacao_fs)

    def obter_todas_transacoes(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            # Buscar na coleção raiz filtrando por user_id usando FieldFilter
            docs = self.db.collection('transacoes').where(filter=FieldFilter('user_id', '==', user_id)).stream()
            transacoes = []
            for doc in docs:
                t = doc.to_dict()
                transacoes.append(t)
            return transacoes
        except Exception as e:
            print(f"Erro ao obter transações: {e}")
            return []

    def obter_transacoes_por_tipo(self, user_id: str, tipo: str) -> List[Dict[str, Any]]:
        todas = self.obter_todas_transacoes(user_id)
        return [t for t in todas if t.get('tipo') == tipo]

    def calcular_saldo(self, user_id: str) -> Decimal:
        receitas = self.obter_transacoes_por_tipo(user_id, 'receita')
        despesas = self.obter_transacoes_por_tipo(user_id, 'despesa')

        total_receitas = sum(Decimal(str(r['valor'])) for r in receitas)
        total_despesas = sum(Decimal(str(d['valor'])) for d in despesas)

        return total_receitas - total_despesas

    def limpar_dados(self, user_id: str) -> None:
        pass
