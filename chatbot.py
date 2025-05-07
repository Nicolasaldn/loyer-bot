from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

# Initialisation du chatbot
chatbot = ChatBot(
    "MonAssistant",
    logic_adapters=[
        "chatterbot.logic.BestMatch"
    ]
)

# Entraînement avec les corpus de base (anglais et français)
trainer_corpus = ChatterBotCorpusTrainer(chatbot)
trainer_corpus.train("chatterbot.corpus.english", "chatterbot.corpus.french")

# Entraînement avec des exemples personnalisés
trainer_personnalise = ListTrainer(chatbot)
trainer_personnalise.train([
    "Je veux une quittance.",
    "Pour quel locataire ?",
    "Je veux un rappel.",
    "Pour quel locataire et quelle date ?",
    "Salut !",
    "Salut ! Comment puis-je t'aider aujourd'hui ?",
    "Comment ça va ?",
    "Ça va très bien, merci ! Et toi ?",
    "Je veux une quittance pour Thomas Cohen.",
    "Pour quelle période ?",
    "Rappel pour Sophie.",
    "Quelle date pour le rappel ?"
])

# Fonction pour obtenir une réponse du chatbot
def get_chatbot_response(message):
    return str(chatbot.get_response(message))
