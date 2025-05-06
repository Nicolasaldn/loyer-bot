# utils/state.py

# Dictionnaire global pour suivre l’état des utilisateurs (mémoire locale)
user_states = {}

def set_user_state(user_id: int, state: dict):
    """Enregistre l’état courant d’un utilisateur"""
    user_states[user_id] = state

def get_user_state(user_id: int) -> dict:
    """Retourne l’état courant d’un utilisateur, ou {} par défaut"""
    return user_states.get(user_id, {})

def clear_user_state(user_id: int):
    """Efface l’état d’un utilisateur"""
    if user_id in user_states:
        del user_states[user_id]
