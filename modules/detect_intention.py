def detect_intent(user_input,model):
    """
    Classifie l'intention utilisateur.
    Renvoie : 'SYMPTOMS', 'URGENT', 'ADMIN', ou 'OTHER'
    """

    intent_definition = """
Catégories possibles :

1. SYMPTOMS :
   L'utilisateur décrit un symptôme ou un problème de santé.
   Exemple1 : "J'ai mal à la tête depuis 2 jours."
   Exemple2 : "Je me sens très fatigué et j'ai de la fièvre."
2. URGENT :
   Situation qu'on juge grave ou dangereuse.
   Exemple1 : "Je n'arrive plus à respirer."
   Exemple2 : "J'ai une douleur très forte dans la poitrine."
3. ADMIN :
   Question administrative ou organisationnelle.
   Exemple1 : "Comment prendre rendez-vous ?"
   Exemple2 : "Quels sont vos horaires d'ouverture ?"
4. OTHER :
   Message hors sujet ou non médical ou une question qui demande de l'information.
   Exemple1 : "Qu'est ce que je dois faire maintenant ?"
   Exemple2 : "Donne moi les médicaments."

   
"""

    full_prompt = f"""
Vous êtes un classificateur d'intention médical.

{intent_definition}

Message utilisateur :
"{user_input}"

Question :
Quelle est l'intention ?

Répondez uniquement par :
SYMPTOMS
URGENT
ADMIN
OTHER

Sans explication.
"""

    response = model.generate_content(full_prompt).text.strip().upper()

    if response in ["SYMPTOMS", "URGENT", "ADMIN", "OTHER"]:
        return response
    else:
        return "OTHER"  # fallback sécurité
