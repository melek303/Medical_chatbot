SYSTEM_PROMPT = """
Tu es un chatbot médical grand public pour le site Tessan.
Ton rôle : fournir des informations médicales générales et fiables.
Tu ne fais jamais de diagnostic, ne prescris jamais de médicaments,
et ne personnalises jamais les réponses.
Si un symptôme critique est détecté, recommande de consulter un médecin.
Style : clair, rassurant, non alarmiste.
Sois bref et précis.
"""

def generate_response( history: list, model,additional_system_prompt="", temperature: float = 0.2) -> str:
    """
    Génère une réponse en prenant en compte tout l'historique.
    history : liste de dictionnaires [{"role": "user"/"assistant", "content": "..."}]
    """

    

    # Reconstruction de la conversation
    conversation_text = ""
    for message in history:
        if message["role"] == "user":
            conversation_text += f"Utilisateur : {message['content']}\n"
        elif message["role"] == "assistant":
            conversation_text += f"Chatbot : {message['content']}\n"

    # Prompt final
    
    
    New_prompt =SYSTEM_PROMPT+ "\n" + additional_system_prompt

    full_prompt = f"""
{New_prompt}

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



    return assistant_reply
