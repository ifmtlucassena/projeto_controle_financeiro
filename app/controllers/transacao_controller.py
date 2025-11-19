from typing import Dict, Any, Tuple
from decimal import Decimal
from flask_login import current_user

from app.models.banco_de_dados import BancoDeDados
from app.models.transacao_factory import TransacaoFactory
from app.adapters.request_adapter import RequestAdapter


class TransacaoController:

    def __init__(self) -> None:
        self._banco = BancoDeDados()

    def criar_transacao(self, form_data: Any) -> Tuple[bool, str]:
        try:
            dados_adaptados = RequestAdapter.adaptar_formulario_transacao(form_data)

            transacao = TransacaoFactory.criar_transacao(**dados_adaptados)

            self._banco.salvar_transacao(current_user.id, transacao.para_dicionario())

            saldo_atual = self._banco.calcular_saldo(current_user.id)

            tipo = transacao.obter_tipo()
            mensagem = (
                f"{tipo.capitalize()} de R$ {transacao.valor:.2f} "
                f"registrada com sucesso! Saldo atual: R$ {saldo_atual:.2f}"
            )

            return True, mensagem

        except ValueError as e:
            return False, f"Erro de validação: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def listar_transacoes(self) -> Dict[str, Any]:
        transacoes = self._banco.obter_todas_transacoes(current_user.id)
        receitas = self._banco.obter_transacoes_por_tipo(current_user.id, 'receita')
        despesas = self._banco.obter_transacoes_por_tipo(current_user.id, 'despesa')

        total_receitas = sum(Decimal(str(r['valor'])) for r in receitas)
        total_despesas = sum(Decimal(str(d['valor'])) for d in despesas)
        saldo = self._banco.calcular_saldo(current_user.id)

        # Garantir que todas as transações sejam serializáveis
        transacoes_serializaveis = []
        for t in transacoes:
            transacao_serializada = {
                'tipo': str(t.get('tipo', '')),
                'valor': float(t.get('valor', 0)),
                'data': str(t.get('data', '')),
                'descricao': str(t.get('descricao', '')),
                'categoria': str(t.get('categoria', ''))
            }
            # Campos específicos por tipo
            if t.get('tipo') == 'receita':
                transacao_serializada['conta_destino'] = str(t.get('conta_destino', ''))
            else:
                transacao_serializada['metodo_pagamento'] = str(t.get('metodo_pagamento', ''))
                transacao_serializada['estabelecimento'] = str(t.get('estabelecimento', ''))
            transacoes_serializaveis.append(transacao_serializada)

        return {
            'transacoes': transacoes_serializaveis,
            'total_receitas': float(total_receitas),
            'total_despesas': float(total_despesas),
            'saldo': float(saldo),
            'quantidade_transacoes': len(transacoes)
        }

    def obter_resumo_financeiro(self) -> Dict[str, Any]:
        receitas = self._banco.obter_transacoes_por_tipo(current_user.id, 'receita')
        despesas = self._banco.obter_transacoes_por_tipo(current_user.id, 'despesa')

        total_receitas = sum(Decimal(str(r['valor'])) for r in receitas)
        total_despesas = sum(Decimal(str(d['valor'])) for d in despesas)
        saldo = self._banco.calcular_saldo(current_user.id)

        return {
            'saldo_atual': float(saldo),
            'total_receitas': float(total_receitas),
            'total_despesas': float(total_despesas),
            'quantidade_receitas': len(receitas),
            'quantidade_despesas': len(despesas)
        }
