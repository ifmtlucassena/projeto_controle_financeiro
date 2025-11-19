# Controle Financeiro Pessoal

Sistema web acadêmico completo para controle de receitas e despesas pessoais com interface visual responsiva e módulo de relatórios.

## Tecnologias

- **Backend**: Python 3.x + Flask
- **Frontend**: HTML5 + Bootstrap 5.3 + JavaScript
- **Template Engine**: Jinja2
- **Armazenamento**: Em memória (sem banco SQL)

## Padrões de Projeto Implementados

- **Singleton**: Gerenciador de dados (`BancoDeDados`)
- **Factory Method**: Criação de transações (`TransacaoFactory`)
- **Adapter**: Conversão de dados web para domínio (`RequestAdapter`)
- **Builder**: Construção de relatórios complexos (`DashboardBuilder`)

## Estrutura do Projeto

```
controle_financeiro/
├── app/
│   ├── adapters/        # Adaptadores (Request → Domain)
│   ├── builders/        # Builders para construção de relatórios
│   ├── controllers/     # Controladores de negócio
│   ├── models/          # Modelos de domínio
│   ├── templates/       # Templates HTML (Jinja2)
│   ├── utils/           # Utilitários
│   └── routes.py        # Definição de rotas
├── run.py               # Arquivo principal
├── test_backend.py      # Testes do backend
├── popular_dados_exemplo.py  # Script para dados de demonstração
├── requirements.txt     # Dependências
├── ETAPA2_DOCUMENTACAO.md  # Documentação Backend
└── ETAPA3_DOCUMENTACAO.md  # Documentação Frontend
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

### 1. Popular com dados de exemplo (recomendado):
```bash
python popular_dados_exemplo.py
```
Isso criará 15 transações de exemplo para demonstração.

### 2. Iniciar o servidor web:
```bash
python run.py
```
A aplicação estará disponível em `http://127.0.0.1:5000`

### 3. Testar o backend (sem servidor):
```bash
python test_backend.py
```

## Funcionalidades

### Dashboard Principal (`/`)
- 📊 Cards com Saldo Atual, Total de Receitas e Despesas
- 📈 Gráficos de resumo por categoria com percentuais
- 📋 Lista de transações recentes
- 📉 Estatísticas (média, maior/menor valor)
- 🎨 Interface responsiva e moderna

### Cadastro de Transação (`/nova-transacao`)
- 📝 Formulário único para Receitas e Despesas
- 🔄 Campos dinâmicos baseados no tipo
- ✅ Validação completa de dados
- 📅 Seletor de data com padrão = hoje
- 🏷️ Categorias pré-definidas

### API Endpoints (JSON)
- `GET /api/resumo` - Resumo financeiro
- `GET /api/transacoes` - Todas transações
- `GET /api/transacoes/<tipo>` - Filtrar por tipo

## Documentação Detalhada

- `ETAPA2_DOCUMENTACAO.md` - Backend, Controllers e Padrões (Singleton, Factory, Adapter)
- `ETAPA3_DOCUMENTACAO.md` - Frontend, Templates e Builder Pattern

## Screenshots

### Dashboard
- Cards de resumo com cores semânticas
- Barras de progresso por categoria
- Tabela responsiva de transações

### Formulário
- Campos dinâmicos (Receita/Despesa)
- Validação em tempo real
- Mensagens de sucesso/erro
