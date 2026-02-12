
def detect_red_flag_llm(user_input,model):
    """
    Envoie au LLM le contexte des red flags et le texte utilisateur.
    Le LLM doit impérativement répondre par 'YES' ou 'NO'.
    """
    final_prompt ="""
Définition :
Un red flag est un symptôme pouvant indiquer une urgence médicale ou une pathologie grave nécessitant une évaluation médicale rapide.

Exemples de red flags :
- Difficulté à respirer ou essoufflement sévère
- Douleur thoracique intense ou oppressante
- Perte de connaissance
- Confusion soudaine
- Convulsions
- Mal de tête brutal et extrêmement intense
- Fièvre > 40°C
- Vomissements avec sang
- Sang dans les selles
- Paralysie ou faiblesse d'un côté du corps

Instruction :
Analysez le message de l'utilisateur.
S'il contient un red flag → répondez uniquement "YES".
Sinon → répondez uniquement "NO".
Aucune explication.

"""

    full_prompt = f"""
Vous êtes un assistant médical virtuel. 
Voici la définition et quelques exemples de red flags médicaux à connaître :
{final_prompt}

Utilisateur : "{user_input}"

Question : Est-ce que le texte de l'utilisateur contient un red flag ?
Répondez impérativement par "YES" ou "NO" uniquement, sans explication.
"""
    # Appel au LLM (exemple générique, adapte selon ton SDK Gemini)
    response = model.generate_content(full_prompt).text.strip()
    # Nettoyage pour garder uniquement YES ou NO
    response = response.upper()
    if "YES" in response:
        return True
    else:
        return False
