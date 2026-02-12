SYSTEM_PROMPT = """
Tu es un chatbot médical grand public pour le site Tessan.
Ton rôle : fournir des informations médicales générales et fiables.
Tu ne fais jamais de diagnostic, ne prescris jamais de médicaments,
et ne personnalises jamais les réponses.
Si un symptôme critique est détecté, recommande de consulter un médecin.
Style : clair, rassurant, non alarmiste.
Sois bref et précis.
"""

def generate_response(user_input: str, history: list, model, temperature: float = 0.3) -> str:
    """
    Génère une réponse en prenant en compte tout l'historique.
    history : liste de dictionnaires [{"role": "user"/"assistant", "content": "..."}]
    """

    # Ajouter le nouveau message utilisateur à l’historique
    history.append({"role": "user", "content": user_input})

    # Reconstruction de la conversation
    conversation_text = ""
    for message in history:
        if message["role"] == "user":
            conversation_text += f"Utilisateur : {message['content']}\n"
        elif message["role"] == "assistant":
            conversation_text += f"Chatbot : {message['content']}\n"

    # Prompt final
    full_prompt = f"""
{SYSTEM_PROMPT}

Historique de conversation :
{conversation_text}

Chatbot :
"""

    response = model.generate_content(
        full_prompt,
        generation_config={
            "temperature": temperature,
            "top_p": 0.9,
        }
    )

    assistant_reply = response.text.strip()

    # Ajouter la réponse du chatbot à l’historique
    history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply
