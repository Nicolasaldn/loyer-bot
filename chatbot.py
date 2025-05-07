import nltk
nltk.download('punkt', quiet=True)

from nltk.chat.util import Chat, reflections

# Simple chatbot avec des patterns de base
pairs = [
    [r"je veux une quittance", ["Pour quel locataire ?"]],
    [r"rappel", ["Pour quel locataire et quelle date ?"]],
    [r"salut", ["Salut ! Comment puis-je t'aider aujourd'hui ?"]],
    [r"comment ça va ?", ["Ça va très bien, merci ! Et toi ?"]],
    [r"merci", ["Avec plaisir !"]],
]

chatbot = Chat(pairs, reflections)

def get_chatbot_response(message):
    response = chatbot.respond(message)
    return response if response else "Désolé, je ne comprends pas ta demande."
