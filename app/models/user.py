from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, uid, email, nome):
        self.id = uid
        self.email = email
        self.nome = nome

    @staticmethod
    def get(user_id):
        # This method will be used by user_loader, but since we are using Firebase,
        # we might need to fetch user data from Firestore or Auth.
        # For simplicity in the loader, we might just reconstruct the user if we store enough in session,
        # or fetch from DB.
        # However, the prompt says "Crie um Model User... que guarda apenas id, email e nome".
        # The actual fetching logic usually resides in the loader function in __init__ or controller.
        return None 
