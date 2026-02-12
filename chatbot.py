# chatbot_main.py
from detect_red_flag import detect_red_flag_llm
from chatbot_response_safety import check_medical_safety
from detect_intention import detect_intent
from should_offer_teleconsultation import should_offer_teleconsultation_llm
from detect_end_of_conversation import detect_end_conversation  # nouveau

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


def run_chatbot(model):

    greeting = "Bonjour ! Je suis là pour vous fournir des informations de santé générales."
    display_message("Assistant", greeting)

    conversation_active = True
    history = []
    history.append({"role": "assistant", "content": greeting})

    log_event("conversation_start", {"greeting": greeting})

    while conversation_active:

        user_input = input("")

        display_message("Patient", user_input)

        log_event("user_message", {"text": user_input})

        # Ajouter le nouveau message utilisateur à l’historique
        history.append({"role": "user", "content": user_input})

        # 1️⃣ Détecter intention
        start_time = time.time()
        intent = detect_intent(user_input, model)
        response_time = time.time() - start_time
        log_event("intent_detected", {"intent": intent}, response_time=response_time)

        if intent == "URGENT":
            message = (
                "Vos symptômes semblent urgents. "
                "Je vous recommande une téléconsultation ou un rendez-vous en urgence."
            )
            display_message("Assistant", message)
            log_event("urgent_detected", {"response": message})
            conversation_active = False
            continue

        elif intent == "ADMIN":
            message = (
                "Pour les questions administratives, veuillez consulter votre espace patient."
            )
            display_message("Assistant", message)
            log_event("admin_detected", {"response": message})
            continue

        # 2️⃣ Détecter red flag
        start_time = time.time()
        red_flag = detect_red_flag_llm(user_input, model)
        response_time = time.time() - start_time
        log_event("red_flag_check", {"red_flag": red_flag}, response_time=response_time)

        if red_flag:
            message = (
                "Vos symptômes pourraient nécessiter une attention rapide. "
                "Je vous recommande une téléconsultation ou un rendez-vous en urgence."
            )
            display_message("Assistant", message)
            log_event("red_flag_triggered", {"response": message})
            conversation_active = False
            continue

        # 3️⃣ Téléconsultation / fin
        start_time = time.time()
        offer_tele = should_offer_teleconsultation_llm(user_input, model)
        end_conv = detect_end_conversation(user_input, model)
        response_time = time.time() - start_time
        log_event("conversation_checks", {
            "offer_teleconsultation": offer_tele,
            "end_conversation": end_conv
        }, response_time=response_time)

        if offer_tele or end_conv:
            response_text = generate_response(history, model)
            start_time = time.time()
            safe = check_medical_safety(response_text, model)
            response_time_safety = time.time() - start_time
            log_event("safety_check", {"safe": safe}, response_time=response_time_safety)

            if not safe:
                message = (
                    "Je ne peux pas fournir de diagnostic ou de prescription. "
                    "Veuillez consulter un professionnel de santé."
                )
                response_text = message
                display_message("Assistant", message)
                log_event("safety_blocked", {"blocked_response": response_text})
                # Ajouter la réponse du chatbot à l’historique
                history.append({"role": "assistant", "content": response_text})
                continue
            response_text += "\n\nSouhaitez-vous passer en téléconsultation maintenant ?"
            # Ajouter la réponse du chatbot à l’historique
            history.append({"role": "assistant", "content": response_text})
            display_message("Assistant", response_text)
            log_event("teleconsultation_proposed", {"response": response_text})

            conversation_active = False
            continue

        # 4️⃣ Génération réponse
        start_time = time.time()
        response_text = generate_response(history, model)
        response_time_generation = time.time() - start_time
        # 5️⃣ Vérification sécurité
        start_time = time.time()
        safe = check_medical_safety(response_text, model)
        response_time_safety = time.time() - start_time
        log_event("safety_check", {"safe": safe}, response_time=response_time_safety)

        if not safe:
            message = (
                "Je ne peux pas fournir de diagnostic ou de prescription. "
                "Veuillez consulter un professionnel de santé."
            )
            response_text = message
            display_message("Assistant", message)
            log_event("safety_blocked", {"blocked_response": response_text})
            # Ajouter la réponse du chatbot à l’historique
            history.append({"role": "assistant", "content": response_text})
            continue

        display_message("Assistant", response_text)
        log_event("assistant_response", {"response": response_text}, response_time=response_time_generation)

    log_event("conversation_end", {"status": "terminated"})
