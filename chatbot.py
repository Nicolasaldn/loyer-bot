from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import nltk
nltk.download('punkt')

# Initialisation du chatbot
chatbot = ChatBot(
    "MonAssistant",
    logic_adapters=[
        "chatterbot.logic.BestMatch"
    ]
)

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
])
