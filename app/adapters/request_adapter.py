from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Any
from werkzeug.datastructures import ImmutableMultiDict


class RequestAdapter:

    @staticmethod
    def adaptar_formulario_transacao(
        form_data: ImmutableMultiDict
    ) -> Dict[str, Any]:
        try:
            tipo = form_data.get('tipo', '').strip()
            valor_str = form_data.get('valor', '').strip()
            data_str = form_data.get('data', '').strip()
            descricao = form_data.get('descricao', '').strip()
            categoria = form_data.get('categoria', '').strip()

            if not tipo:
                raise ValueError("O campo 'tipo' é obrigatório")
            if not valor_str:
                raise ValueError("O campo 'valor' é obrigatório")
            if not data_str:
                raise ValueError("O campo 'data' é obrigatório")
            if not descricao:
                raise ValueError("O campo 'descrição' é obrigatório")
            if not categoria:
                raise ValueError("O campo 'categoria' é obrigatório")

            try:
                valor_limpo = valor_str.replace(',', '.').strip()
                valor = Decimal(valor_limpo)
                if valor <= 0:
                    raise ValueError("O valor deve ser maior que zero")
            except (InvalidOperation, ValueError):
                raise ValueError(f"Valor inválido: '{valor_str}'. Use formato numérico (ex: 100.50)")

            try:
                data = datetime.strptime(data_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Data inválida: '{data_str}'. Use formato YYYY-MM-DD (ex: 2024-01-15)")

            dados_adaptados: Dict[str, Any] = {
                'tipo': tipo,
                'valor': valor,
                'data': data,
                'descricao': descricao,
                'categoria': categoria
            }

            if tipo.lower() == 'receita':
                conta_destino = form_data.get('conta_destino', '').strip()
                if not conta_destino:
                    raise ValueError("O campo 'conta_destino' é obrigatório para receitas")
                dados_adaptados['conta_destino'] = conta_destino
            elif tipo.lower() == 'despesa':
                metodo_pagamento = form_data.get('metodo_pagamento', '').strip()
                estabelecimento = form_data.get('estabelecimento', '').strip()
                if not metodo_pagamento:
                    raise ValueError("O campo 'metodo_pagamento' é obrigatório para despesas")
                if not estabelecimento:
                    raise ValueError("O campo 'estabelecimento' é obrigatório para despesas")
                dados_adaptados['metodo_pagamento'] = metodo_pagamento
                dados_adaptados['estabelecimento'] = estabelecimento
            else:
                raise ValueError(f"Tipo inválido: '{tipo}'. Tipos válidos: 'receita' ou 'despesa'")

            return dados_adaptados

        except (ValueError, InvalidOperation) as e:
            raise ValueError(f"Erro ao processar dados do formulário: {str(e)}")
