from flask import current_app
from flask_login import login_user, logout_user
from firebase_admin import auth, firestore, exceptions
import requests
from app.models.user import User

class AuthController:

    def __init__(self):
        self._erro_traducoes = {
            'EMAIL_EXISTS': 'Este email já está cadastrado.',
            'INVALID_EMAIL': 'Email inválido.',
            'WEAK_PASSWORD': 'Senha muito fraca. Use pelo menos 6 caracteres.',
            'EMAIL_NOT_FOUND': 'Email não encontrado.',
            'INVALID_PASSWORD': 'Senha incorreta.',
            'INVALID_LOGIN_CREDENTIALS': 'Email ou senha incorretos.',
            'USER_DISABLED': 'Esta conta foi desativada.',
            'TOO_MANY_ATTEMPTS_TRY_LATER': 'Muitas tentativas. Tente novamente mais tarde.',
            'OPERATION_NOT_ALLOWED': 'Operação não permitida.',
        }

    def _traduzir_erro(self, mensagem_erro: str) -> str:
        """Traduz mensagens de erro do Firebase para PT-BR."""
        for codigo, traducao in self._erro_traducoes.items():
            if codigo in mensagem_erro:
                return traducao
        return f"Erro: {mensagem_erro}"

    def login(self, email, password):
        try:
            api_key = current_app.config.get('FIREBASE_WEB_API_KEY')
            if not api_key:
                return False, "API Key não configurada."

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload)
            data = response.json()

            if 'error' in data:
                erro_msg = data['error'].get('message', 'Erro desconhecido')
                return False, self._traduzir_erro(erro_msg)

            uid = data['localId']
            user_record = auth.get_user(uid)

            user = User(uid=uid, email=email, nome=user_record.display_name or email)
            login_user(user)
            return True, "Login realizado com sucesso!"
        except exceptions.FirebaseError as e:
            return False, self._traduzir_erro(str(e))
        except Exception as e:
            return False, f"Erro ao fazer login: {str(e)}"

    def register(self, email, password, nome):
        try:
            # Criar usuário no Firebase Authentication
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=nome
            )

            # Criar documento do usuário na coleção raiz 'usuarios'
            db = firestore.client()
            db.collection('usuarios').document(user_record.uid).set({
                'email': email,
                'nome': nome,
                'criado_em': firestore.SERVER_TIMESTAMP
            })

            return True, "Usuário criado com sucesso! Faça login."
        except exceptions.FirebaseError as e:
            erro_str = str(e)
            # Tratar erros específicos do Firebase Admin
            if 'EMAIL_EXISTS' in erro_str or 'already exists' in erro_str.lower():
                return False, "Este email já está cadastrado."
            elif 'WEAK_PASSWORD' in erro_str or 'password' in erro_str.lower():
                return False, "Senha muito fraca. Use pelo menos 6 caracteres."
            elif 'INVALID_EMAIL' in erro_str:
                return False, "Email inválido."
            return False, f"Erro ao criar conta: {erro_str}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    def logout(self):
        logout_user()
