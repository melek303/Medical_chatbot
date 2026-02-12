# Définition et exemples pour le LLM
teleconsultation_definition = """
Un utilisateur devrait se voir proposer une téléconsultation s'il présente l'un des critères suivants :
- est anxieux ou inquiet concernant ses symptômes
- n'est pas à l'aise ou exprime de l'inquiétude
- ses symptômes persistent depuis plusieurs jours
"""

teleconsultation_examples = """
Exemples sécurisés :
1. "J'ai mal au dos depuis 3 jours et je suis inquiet." → YES
2. "Je ne sais pas quoi faire, ça m'inquiète." → YES
3. "Merci, c'est bon pour moi." → YES
4. "J'ai mal au ventre depuis ce matin." → NO
"""

def should_offer_teleconsultation_llm(user_input,model):
    """
    Utilise un LLM pour décider si l'utilisateur doit se voir proposer une téléconsultation.
    Le LLM doit répondre impérativement par YES ou NO.
    """
    prompt = f"""
Vous êtes un assistant médical virtuel.
Voici la définition de quand proposer une téléconsultation :
{teleconsultation_definition}

Exemples :
{teleconsultation_examples}

Texte utilisateur :
"{user_input}"

Question : Selon les règles ci-dessus, l'utilisateur devrait-il se voir proposer une téléconsultation ?
Répondez uniquement par YES ou NO.
"""
    response = model.generate_content(prompt).text.strip().upper()
    
    if "YES" in response:
        return True
    elif "NO" in response:
        return False
    else:
        # fallback si le LLM ne respecte pas la consigne
        return False


