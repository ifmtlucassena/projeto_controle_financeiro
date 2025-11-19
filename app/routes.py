from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app.controllers.transacao_controller import TransacaoController
from app.controllers.auth_controller import AuthController
from app.builders.dashboard_builder import DashboardBuilder
from app.models.banco_de_dados import BancoDeDados


bp = Blueprint('main', __name__)

transacao_controller = TransacaoController()
auth_controller = AuthController()


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        success, message = auth_controller.login(email, password)
        if success:
            return redirect(url_for('main.index'))
        flash(message, 'error')
    
    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nome = request.form.get('nome')
        success, message = auth_controller.register(email, password, nome)
        if success:
            flash(message, 'success')
            return redirect(url_for('main.login'))
        flash(message, 'error')
        
    return render_template('register.html')


@bp.route('/logout')
@login_required
def logout():
    auth_controller.logout()
    return redirect(url_for('main.login'))


@bp.route('/')
@login_required
def index():
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        categoria = request.args.get('categoria')

        # Default dates: Current month
        if not data_inicio:
            today = datetime.now()
            data_inicio = today.replace(day=1).strftime('%Y-%m-%d')

        if not data_fim:
            today = datetime.now()
            data_fim = today.strftime('%Y-%m-%d')

        builder = DashboardBuilder()

        # Always apply filters if dates are present (which they should be now)
        builder.com_filtros(
            data_inicio=data_inicio,
            data_fim=data_fim,
            categoria=categoria
        )

        dados_dashboard = (builder
                          .com_saldo_total()
                          .com_transacoes_recentes()
                          .com_resumo_por_categoria()
                          .com_estatisticas_adicionais()
                          .com_dados_grafico()
                          .build())

        # Passar as datas de filtro para o template
        dados_dashboard['data_inicio'] = data_inicio
        dados_dashboard['data_fim'] = data_fim
        dados_dashboard['categoria_selecionada'] = categoria or 'todas'

        return render_template('index.html', **dados_dashboard)

    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        today = datetime.now()
        return render_template('index.html',
                             saldo_total=0,
                             total_receitas=0,
                             total_despesas=0,
                             transacoes_recentes=[],
                             resumo_por_categoria={'receitas': [], 'despesas': []},
                             quantidade_receitas=0,
                             quantidade_despesas=0,
                             dados_grafico={},
                             filtros_ativos={},
                             data_inicio=today.replace(day=1).strftime('%Y-%m-%d'),
                             data_fim=today.strftime('%Y-%m-%d'),
                             categoria_selecionada='todas')


@bp.route('/nova-transacao', methods=['GET'])
@login_required
def nova_transacao_form():
    return render_template('cadastro.html')


@bp.route('/nova-transacao', methods=['POST'])
@login_required
def nova_transacao_submit():
    try:
        sucesso, mensagem = transacao_controller.criar_transacao(request.form)

        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('main.index'))
        else:
            flash(mensagem, 'error')
            return redirect(url_for('main.nova_transacao_form'))

    except Exception as e:
        flash(f'Erro inesperado: {str(e)}', 'error')
        return redirect(url_for('main.nova_transacao_form'))


@bp.route('/api/resumo')
@login_required
def api_resumo():
    try:
        resumo = transacao_controller.obter_resumo_financeiro()
        return jsonify(resumo)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/api/transacoes')
@login_required
def api_transacoes():
    try:
        dados = transacao_controller.listar_transacoes()
        return jsonify(dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@bp.route('/api/transacoes/<tipo>')
@login_required
def api_transacoes_por_tipo(tipo):
    try:
        banco = BancoDeDados()
        transacoes = banco.obter_transacoes_por_tipo(current_user.id, tipo)

        # Garantir serialização
        transacoes_serializaveis = []
        for t in transacoes:
            transacao_serializada = {
                'tipo': str(t.get('tipo', '')),
                'valor': float(t.get('valor', 0)),
                'data': str(t.get('data', '')),
                'descricao': str(t.get('descricao', '')),
                'categoria': str(t.get('categoria', ''))
            }
            if tipo == 'receita':
                transacao_serializada['conta_destino'] = str(t.get('conta_destino', ''))
            else:
                transacao_serializada['metodo_pagamento'] = str(t.get('metodo_pagamento', ''))
                transacao_serializada['estabelecimento'] = str(t.get('estabelecimento', ''))
            transacoes_serializaveis.append(transacao_serializada)

        return jsonify({
            'tipo': tipo,
            'transacoes': transacoes_serializaveis,
            'quantidade': len(transacoes)
        })
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
