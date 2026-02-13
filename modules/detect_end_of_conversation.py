
def detect_end_conversation(user_input,model):
    """
    Détecte si l'utilisateur souhaite terminer la conversation.
    Retourne True si oui, False sinon.
    """

    definition = """
Un message est considéré comme une fin de conversation si l'utilisateur :

- dit merci sans poser de nouvelle question
- dit au revoir
- indique qu'il n'a plus de questions
- confirme que l'information reçue est suffisante
- accepte une téléconsultation
"""

    examples = """
Exemples FIN :
- "Merci beaucoup."
- "C'est bon, j'ai compris."
- "Je n'ai plus de questions."
- "Au revoir."
- "Oui je veux une téléconsultation."

Exemples NON FIN :
- "Merci, mais j'ai encore une question."
- "Et si la douleur continue ?"
- "Que dois-je faire maintenant ?"
"""

    full_prompt = f"""
Vous êtes un classificateur.

{definition}

{examples}

Message utilisateur :
"{user_input}"

Est-ce une fin de conversation ?

Répondez uniquement par :
YES
NO
Sans explication.
"""

    response =  model.generate_content(full_prompt).text.strip().upper()
    if "YES" in response :
        return True
    else:
        return False
