# utils/state.py

user_states = {}

def set_user_state(user_id: int, state: dict):
    """Initialise l’état complet d’un utilisateur."""
    user_states[user_id] = state

def get_user_state(user_id: int) -> dict:
    """Retourne l’état courant d’un utilisateur (vide par défaut)."""
    return user_states.get(user_id, {})

def clear_user_state(user_id: int):
    """Efface l’état de l’utilisateur."""
    if user_id in user_states:
        del user_states[user_id]

def update_user_state(user_id: int, key: str, value):
    """Met à jour une clé spécifique dans l’état utilisateur."""
    if user_id in user_states:
        user_states[user_id][key] = value
