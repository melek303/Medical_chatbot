# chatbot_main.py
from detect_red_flag import detect_red_flag_llm
from chatbot_response_safety import check_medical_safety
from detect_intention import detect_intent
from should_offer_teleconsultation import should_offer_teleconsultation_llm
from detect_end_of_conversation import detect_end_conversation  

from medical_assistant import generate_response

import json
import time

from IPython.display import display, HTML

def display_message(role, message):
    if role == "Assistant":
        color = "#e3f2fd"
        align = "left"
        name = "🤖 Assistant"
    else:
        color = "#d4edda"
        align = "right"
        name = "🧑 Patient"

    # échappe les caractères HTML sensibles et remplace \n par <br>
    message = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    html = f"""
    <div style="
        background-color:{color};
        padding:10px;
        border-radius:10px;
        margin:5px;
        width:60%;
        text-align:left;
        float:{align};
        clear:both;
    ">
        <b>{name} :</b><br>
        {message}
    </div>
    """

    display(HTML(html))

def log_event(event_type, data,response_time = 0, log_file="chat_logs.jsonl"):
    log_entry = {
        "response time": response_time,
        "event_type": event_type,
        "data": data
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def generate_safe_response(history, model):
    """
    Génère une réponse et effectue la vérification de sécurité avec deuxième chance,
    en loggant chaque étape.
    """
    # Première réponse
    response_text = generate_response(history, model)
    start_time = time.time()
    safe = check_medical_safety(response_text, model)
    log_event("safety_check", {"safe": safe},response_time=time.time() - start_time)

    if safe:
        return response_text, True

    # Identifier la cause
    prompt_cause = (
        f"La réponse suivante a été refusée car elle n'est pas safe :\n{response_text}\n"
        "Indique en une seule phrase la cause du refus : diagnostic, prescription, bilan ou autre, "
        "et le passage précis refusé."
    )
    additional_prompt = model.generate_content(prompt_cause).text.strip()
    log_event("failure cause", {"cause": additional_prompt})
    # Deuxième chance
    additional_system_prompt = (
        f"Voici la réponse refusée :\n"
        f"Debut reponse refusée\n"
        f"{response_text}\n"
        f"fin reponse refusée\n"
        f"{additional_prompt}\n"
        "Génère maintenant une réponse informative, claire, rassurante, "
        "sans diagnostic, prescription ou bilan, en reformulant les informations utiles si possible."
    )
    response_text = generate_response(history, model, additional_system_prompt=additional_system_prompt,temperature=0.1)
    start_time = time.time()
    safe2 = check_medical_safety(response_text, model)
    log_event("safety_check_second_chance", {"safe": safe2},response_time=time.time() - start_time)

    if safe2:
        return response_text, True

    # Blocage si deuxième chance échoue
    response_text = (
        "Je ne peux pas fournir de diagnostic ou de prescription. "
        "Veuillez consulter un professionnel de santé."
    )
    log_event("safety_blocked", {"blocked_response": response_text})
    return response_text, False



def run_chatbot(model):
    greeting = "Bonjour ! Je suis là pour vous fournir des informations de santé générales."
    display_message("Assistant", greeting)

    conversation_active = True
    history = [{"role": "assistant", "content": greeting}]
    log_event("conversation_start", {"greeting": greeting})

    while conversation_active:
        user_input = input("")
        display_message("Patient", user_input)
        log_event("user_message", {"text": user_input})

        # Ajouter le message utilisateur à l’historique
        history.append({"role": "user", "content": user_input})

        # 1️⃣ Détecter intention
        start_time = time.time()
        intent = detect_intent(user_input, model)
        log_event("intent_detected", {"intent": intent}, response_time=time.time() - start_time)

        if intent == "URGENT":
            conversation_active = False

            message = (
                "Vos symptômes semblent urgents. "
                "Je vous recommande une téléconsultation ou un rendez-vous en urgence."
            )
            display_message("Assistant", message)
            log_event("urgent_detected", {"response": message})
            
            history.append({"role": "assistant", "content": message})
            continue

        elif intent == "ADMIN":
            message = (
                "Pour les questions administratives, veuillez consulter votre espace patient."
            )
            display_message("Assistant", message)
            log_event("admin_detected", {"response": message})
            history.append({"role": "assistant", "content": message})
            continue

        # 2️⃣ Détecter red flag
        start_time = time.time()
        red_flag = detect_red_flag_llm(user_input, model)
        log_event("red_flag_check", {"red_flag": red_flag}, response_time=time.time() - start_time)

        if red_flag:
            conversation_active = False

            message = (
                "Vos symptômes pourraient nécessiter une attention rapide. "
                "Souhaitez-vous passer en téléconsultation maintenant ?"
            )
            display_message("Assistant", message)
            log_event("red_flag_triggered", {"response": message})
            history.append({"role": "assistant", "content": message})
            continue

        # 3️⃣ Téléconsultation / fin
        start_time = time.time()
        offer_tele = should_offer_teleconsultation_llm(user_input, model)
        end_conv = detect_end_conversation(user_input, model)
        log_event("conversation_checks", {
            "offer_teleconsultation": offer_tele,
            "end_conversation": end_conv
        }, response_time=time.time() - start_time)

        if offer_tele or end_conv:
            # Génération initiale + sécurité avec deuxième chance
            response_text, safe = generate_safe_response(history, model)

            # Ajouter la réponse finale à l’historique
            history.append({"role": "assistant", "content": response_text})

            # Affichage avec question téléconsultation
            display_text = response_text + "\n\nSouhaitez-vous passer en téléconsultation maintenant ?"
            display_message("Assistant", display_text)
            log_event("teleconsultation_proposed", {"response": display_text})

            conversation_active = False
            continue

        # 4️⃣ Génération réponse normale + sécurité
        start_time = time.time()
        response_text, safe = generate_safe_response(history, model)
        end_time = time.time()
        # Ajouter la réponse normale à l’historique
        history.append({"role": "assistant", "content": response_text})

        # Affichage normal
        display_message("Assistant", response_text)
        log_event("assistant_response", {"response": response_text}, response_time=end_time - start_time)
    
    log_event("conversation_end", {"status": "terminated"})



