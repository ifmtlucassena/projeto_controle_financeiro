import json
from decimal import Decimal
from datetime import datetime, date
from typing import Any
import types


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, date):
            return obj.isoformat()

        # Tratar métodos e funções que foram passados sem serem chamados
        if isinstance(obj, (types.MethodType, types.FunctionType, types.BuiltinMethodType, types.BuiltinFunctionType)):
            # Tentar chamar o método sem argumentos
            try:
                result = obj()
                return self.default(result) if not isinstance(result, (str, int, float, bool, list, dict, type(None))) else result
            except:
                return str(obj)

        # Tratar outros tipos não serializáveis
        try:
            return str(obj)
        except:
            return super().default(obj)


def converter_para_tipos_nativos(dados: dict) -> dict:
    if 'valor' in dados and isinstance(dados['valor'], (int, float)):
        dados['valor'] = Decimal(str(dados['valor']))

    return dados
