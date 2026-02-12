import os
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API depuis .env
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("La clé GEMINI_API_KEY est introuvable dans le fichier .env")

# Configurer Gemini
genai.configure(api_key=api_key)

# Créer le modèle
model = genai.GenerativeModel("models/gemini-2.5-flash")
