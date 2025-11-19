from typing import Dict, Any, List, Optional
from decimal import Decimal
from collections import defaultdict
from datetime import datetime

from app.models.banco_de_dados import BancoDeDados
from flask_login import current_user


class DashboardBuilder:

    def __init__(self) -> None:
        self._banco = BancoDeDados()
        self._transacoes_filtradas: Optional[List[Dict[str, Any]]] = None
        self._user_id = current_user.id if current_user and current_user.is_authenticated else None
        self.reset()

    def reset(self) -> 'DashboardBuilder':
        self._dados: Dict[str, Any] = {
            'saldo_total': 0.0,
            'total_receitas': 0.0,
            'total_despesas': 0.0,
            'transacoes_recentes': [],
            'resumo_por_categoria': {'receitas': [], 'despesas': []},
            'quantidade_receitas': 0,
            'quantidade_despesas': 0,
            'ultima_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'dados_grafico': {
                'receitas_vs_despesas': {
                    'labels': ['Receitas', 'Despesas'],
                    'data': [0.0, 0.0],
                    'colors': ['#10b981', '#ef4444']
                },
                'despesas_por_categoria': {
                    'labels': [],
                    'data': [],
                    'color': '#ef4444'
                },
                'receitas_por_categoria': {
                    'labels': [],
                    'data': [],
                    'color': '#10b981'
                }
            },
            'filtros_ativos': {},
            'estatisticas': {
                'valor_medio': 0.0,
                'maior_transacao': 0.0,
                'menor_transacao': 0.0,
                'total_transacoes': 0
            }
        }
        self._transacoes_filtradas = None
        return self

    def com_saldo_total(self) -> 'DashboardBuilder':
        transacoes = self._obter_transacoes()

        receitas = [t for t in transacoes if t['tipo'] == 'receita']
        despesas = [t for t in transacoes if t['tipo'] == 'despesa']

        total_receitas = sum(Decimal(str(r['valor'])) for r in receitas)
        total_despesas = sum(Decimal(str(d['valor'])) for d in despesas)
        saldo = total_receitas - total_despesas

        self._dados['saldo_total'] = float(saldo)
        self._dados['total_receitas'] = float(total_receitas)
        self._dados['total_despesas'] = float(total_despesas)
        self._dados['quantidade_receitas'] = len(receitas)
        self._dados['quantidade_despesas'] = len(despesas)

        return self

    def com_transacoes_recentes(self, limite: int = 10) -> 'DashboardBuilder':
        transacoes = self._obter_transacoes()

        transacoes_ordenadas = sorted(
            transacoes,
            key=lambda t: datetime.fromisoformat(t['data']),
            reverse=True
        )

        transacoes_formatadas = []
        for t in transacoes_ordenadas[:limite]:
            data_obj = datetime.fromisoformat(t['data'])
            transacao_formatada = {
                'tipo': str(t['tipo']),
                'descricao': str(t['descricao']),
                'valor': float(t['valor']),
                'categoria': str(t['categoria']),
                'data': data_obj.strftime('%d/%m/%Y'),
                'data_iso': str(t['data'])
            }

            if t['tipo'] == 'receita':
                transacao_formatada['conta_destino'] = str(t.get('conta_destino', '-'))
            else:
                transacao_formatada['metodo_pagamento'] = str(t.get('metodo_pagamento', '-'))
                transacao_formatada['estabelecimento'] = str(t.get('estabelecimento', '-'))

            transacoes_formatadas.append(transacao_formatada)

        self._dados['transacoes_recentes'] = transacoes_formatadas
        return self

    def com_resumo_por_categoria(self) -> 'DashboardBuilder':
        transacoes = self._obter_transacoes()
        receitas = [t for t in transacoes if t['tipo'] == 'receita']
        despesas = [t for t in transacoes if t['tipo'] == 'despesa']

        receitas_por_categoria: Dict[str, Decimal] = defaultdict(Decimal)
        for receita in receitas:
            categoria = receita.get('categoria', 'Sem Categoria')
            valor = Decimal(str(receita['valor']))
            receitas_por_categoria[categoria] += valor

        despesas_por_categoria: Dict[str, Decimal] = defaultdict(Decimal)
        for despesa in despesas:
            categoria = despesa.get('categoria', 'Sem Categoria')
            valor = Decimal(str(despesa['valor']))
            despesas_por_categoria[categoria] += valor

        total_despesas = sum(despesas_por_categoria.values())

        despesas_com_percentual = []
        for categoria, valor in despesas_por_categoria.items():
            percentual = (valor / total_despesas * 100) if total_despesas > 0 else 0
            despesas_com_percentual.append({
                'categoria': categoria,
                'valor': float(valor),
                'percentual': float(percentual)
            })

        despesas_com_percentual.sort(key=lambda x: x['valor'], reverse=True)

        receitas_formatadas = [
            {'categoria': cat, 'valor': float(val)}
            for cat, val in receitas_por_categoria.items()
        ]
        receitas_formatadas.sort(key=lambda x: x['valor'], reverse=True)

        self._dados['resumo_por_categoria'] = {
            'receitas': receitas_formatadas,
            'despesas': despesas_com_percentual
        }

        return self

    def com_estatisticas_adicionais(self) -> 'DashboardBuilder':
        transacoes = self._obter_transacoes()

        if transacoes:
            valores = [Decimal(str(t['valor'])) for t in transacoes]
            valor_medio = sum(valores) / len(valores)

            maior_transacao = max(valores)
            menor_transacao = min(valores)

            self._dados['estatisticas'] = {
                'valor_medio': float(valor_medio),
                'maior_transacao': float(maior_transacao),
                'menor_transacao': float(menor_transacao),
                'total_transacoes': len(transacoes)
            }
        else:
            self._dados['estatisticas'] = {
                'valor_medio': 0.0,
                'maior_transacao': 0.0,
                'menor_transacao': 0.0,
                'total_transacoes': 0
            }

        return self

    def com_filtros(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        categoria: Optional[str] = None
    ) -> 'DashboardBuilder':
        transacoes = self._banco.obter_todas_transacoes(self._user_id)
        transacoes_filtradas = transacoes.copy()

        filtros_ativos = {}

        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                transacoes_filtradas = [
                    t for t in transacoes_filtradas
                    if datetime.fromisoformat(t['data']) >= data_inicio_obj
                ]
                filtros_ativos['data_inicio'] = data_inicio_obj.strftime('%d/%m/%Y')
            except ValueError:
                pass

        if data_fim:
            try:
                # Adicionar 23:59:59 para incluir o dia inteiro
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').replace(
                    hour=23, minute=59, second=59
                )
                transacoes_filtradas = [
                    t for t in transacoes_filtradas
                    if datetime.fromisoformat(t['data']) <= data_fim_obj
                ]
                filtros_ativos['data_fim'] = data_fim_obj.strftime('%d/%m/%Y')
            except ValueError:
                pass

        if categoria and categoria != 'todas':
            transacoes_filtradas = [
                t for t in transacoes_filtradas
                if t.get('categoria', '').lower() == categoria.lower()
            ]
            filtros_ativos['categoria'] = categoria

        self._transacoes_filtradas = transacoes_filtradas
        self._dados['filtros_ativos'] = filtros_ativos

        return self

    def com_dados_grafico(self) -> 'DashboardBuilder':
        transacoes = self._obter_transacoes()

        receitas = [t for t in transacoes if t['tipo'] == 'receita']
        despesas = [t for t in transacoes if t['tipo'] == 'despesa']

        total_receitas = sum(Decimal(str(r['valor'])) for r in receitas)
        total_despesas = sum(Decimal(str(d['valor'])) for d in despesas)

        grafico_receitas_despesas = {
            'labels': ['Receitas', 'Despesas'],
            'data': [float(total_receitas), float(total_despesas)],
            'colors': ['#10b981', '#ef4444']
        }

        despesas_por_categoria: Dict[str, Decimal] = defaultdict(Decimal)
        for despesa in despesas:
            categoria = despesa.get('categoria', 'Sem Categoria')
            valor = Decimal(str(despesa['valor']))
            despesas_por_categoria[categoria] += valor

        categorias_ordenadas = sorted(
            despesas_por_categoria.items(),
            key=lambda x: x[1],
            reverse=True
        )[:8]

        grafico_categorias = {
            'labels': [cat for cat, _ in categorias_ordenadas],
            'data': [float(val) for _, val in categorias_ordenadas],
            'color': '#ef4444'
        }

        receitas_por_categoria: Dict[str, Decimal] = defaultdict(Decimal)
        for receita in receitas:
            categoria = receita.get('categoria', 'Sem Categoria')
            valor = Decimal(str(receita['valor']))
            receitas_por_categoria[categoria] += valor

        categorias_receitas_ordenadas = sorted(
            receitas_por_categoria.items(),
            key=lambda x: x[1],
            reverse=True
        )[:8]

        grafico_receitas_categorias = {
            'labels': [cat for cat, _ in categorias_receitas_ordenadas],
            'data': [float(val) for _, val in categorias_receitas_ordenadas],
            'color': '#10b981'
        }

        self._dados['dados_grafico'] = {
            'receitas_vs_despesas': grafico_receitas_despesas,
            'despesas_por_categoria': grafico_categorias,
            'receitas_por_categoria': grafico_receitas_categorias
        }

        return self

    def _obter_transacoes(self) -> List[Dict[str, Any]]:
        if self._transacoes_filtradas is not None:
            return self._transacoes_filtradas
        return self._banco.obter_todas_transacoes(self._user_id)

    def build(self) -> Dict[str, Any]:
        return self._dados.copy()

    def build_completo(self) -> Dict[str, Any]:
        return (self.reset()
                .com_saldo_total()
                .com_transacoes_recentes()
                .com_resumo_por_categoria()
                .com_estatisticas_adicionais()
                .com_dados_grafico()
                .build())
