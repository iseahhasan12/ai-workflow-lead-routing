from datetime import datetime
import uuid
import os
import csv
import joblib

SERVICE_MODEL_PATH = "service_classifier.joblib"

if os.path.exists(SERVICE_MODEL_PATH):
    service_model = joblib.load(SERVICE_MODEL_PATH)
else:
    service_model = None

def validate_input (name, phone, message):      # check if name, phone and message are not empty:
    missing_fields = []
    
    if not name or not name.strip():
        missing_fields.append("name")
    if not phone or not phone.strip():
        missing_fields.append("phone")
    if not message or not message.strip():
        missing_fields.append("message")

    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields

def detect_language(message):       # basic language detection based on keywords. Might want to consider language detection libraries in the future:
    if not message or not message.strip():
        return "unknown"
    message_lower = message.lower()

    if any(word in message_lower for word in ["necesito", "ayuda", "urgente", "fuga", "aire", "acondicionado", "reparación", "hoy", "mañana"]):
        return "Spanish"
    else:
        return "English"
    
def detect_spam(message):       # basic spam detection based on obvious spammy keywords:
    if not message:
        return True, "empty_message"
    
    message_lower = message.lower().strip()
    spam_keywords = ["free", "win", "winner", "prize", "click here", "subscribe", "buy now", "limited time offer", "asdf", "qwer", "zxcv", "lorem ipsum", "12345"]
    
    if len(message_lower) < 5:
        return True, "too_short"
    
    for keyword in spam_keywords:
        if keyword in message_lower:
            return True, f"contains_spam_keyword: {keyword}"
        
    symbol_count = sum(1 for char in message if not char.isalnum() and not char.isspace())
    if len(message) > 0 and symbol_count / len(message) > .4:
        return True, "too_many_symbols"
    return False, "not_spam"


def classify_service_rules(message):      # basic service classification based on keywords. In the future, could consider more advanced NLP techniques or ML models for better accuracy:
    if not message:
        return "General", "low"
    
    message_lower = message.lower()

    plumbing_keywords = ["plumbing", "leak", "pipe", "drain", "clog", "water heater", "faucet", "flood", "toilet", "fuga", "tubería", "desagüe", "calentador de agua", "grifo", "inodoro"]
    ac_keywords = ["air conditioning", "ac", "hvac", "cooling", "refrigeration", "aire acondicionado", "enfriamiento", "refrigeración"]
    electrical_keywords = ["electrical", "electrician", "wiring", "circuit", "outlet", "light", "switch", "eléctrico", "electricista", "cableado", "circuito", "enchufe", "luz", "interruptor"]

    for word in plumbing_keywords:
        if word in message_lower:
            return "Plumbing", "high"
        
    for word in ac_keywords:
        if word in message_lower:
            return "HVAC", "high"
        
    for word in electrical_keywords:
        if word in message_lower:
            return "Electrical", "high"
    return "General", "low"

def classify_service(message):      # improved service classification using a trained ML model:
    if not message or not message.strip():
        return "General", "low", "rules_fallback"
    
    if service_model is None:
        label, conf = classify_service_rules(message)
        return label, conf, "rules_fallback"
    
    predicted_label = service_model.predict([message])[0]

    if hasattr(service_model, "predict_proba"):
        probs = service_model.predict_proba([message])[0]
        prob_max = max(probs)
    else:
        prob_max = .6  # default confidence if model doesn't support predict_proba

    if prob_max >= .6:
        return predicted_label, "high", "ml"
    elif prob_max >= .4:
        return predicted_label, "medium", "ml"
    
    label, conf = classify_service_rules(message)
    return label, conf, "rules_fallback"


def detect_urgency(message, timeline):      # determine urgency based on keywords and timeline:
    #if not message:
    #    return "General", "low"
    
    message_lower = message.lower() if message else ""
    timeline_lower = timeline.lower() if timeline else ""

    urgent_keywords = ["urgent", "asap", "immediately", "emergency", "right now", "no power", "flooding", "hoy", "mañana", "urgente", "inmediatamente", "emergencia", "ahora mismo", "sin energía", "inundación"]
    for word in urgent_keywords:
        if word in message_lower:
            return "High"
        
    if timeline_lower in ["today", "asap", "immediately", "hoy", "inmediatamente"]:
        return "High"
    if timeline_lower in ["this week", "soon", "pronto", "esta semana"]:
        return "Medium"
    return "Low"

def decide_next_action(is_valid, spam_flag, service_cat, urgency, conf):     # decide next steps based on validation, spam detection, service classification and urgency:
    if not is_valid:
        return "request_missing_info"
    if spam_flag:
        return "flag_for_review"
    if urgency == "High":
        return "priority_follow_up"
    if service_cat == "General" and conf == "low":
        return "manual_review"
    return "send_to_booking"

def process_lead(name, phone, message, timeline, source="website_form"):
    lead_id = str(uuid.uuid4())[:8]  # generate a short unique ID for the lead
    timestamp = datetime.now().isoformat(timespec="seconds")
    is_valid, missing_fields = validate_input(name, phone, message)
    language = detect_language(message)
    spam_flag, spam_reason = detect_spam(message)
    service_cat, conf, classification_method = classify_service(message)
    urgency = detect_urgency(message, timeline)
    next_action = decide_next_action(is_valid, spam_flag, service_cat, urgency, conf)

    qualification_result = "Qualified"
    err_reason = ""

    if not is_valid:
        qualification_result = "Incomplete"
        err_reason = f"Missing fields: {', '.join(missing_fields)}"
    elif spam_flag:
        qualification_result = "Suspicious"
        err_reason = spam_reason
    elif service_cat == "General" and conf == "low":
        qualification_result = "Needs Review"
        err_reason = "Low confidence in service classification"
    
    booking_outcome = "pending"
    follow_up_action = "none"
    crm_status = "created"
    lead_stage = "new"
    lead_owner = "unassigned"
    session_terminated = False
    block_recommended = False
    review_required = False

    if qualification_result == "Qualified":
        lead_stage = "qualified"
        if urgency == "High":
            booking_outcome = "priority_callback_required"
            follow_up_action = "immediate_internal_follow_up"
        else:
            booking_outcome = "booking_link_sent"
            follow_up_action = "send_booking_link"
    
    elif qualification_result == "Incomplete": 
        lead_stage = "incomplete"
        crm_status = "needs_update"
        booking_outcome = "not_ready"
        follow_up_action = "request_missing_info"

    elif qualification_result == "Suspicious":
        lead_stage = "blocked_review"
        crm_status = "flagged"
        booking_outcome = "blocked_from_booking"
        follow_up_action = "do_not_follow_up"
        session_terminated = True
        block_recommended = True
        review_required = True

    elif qualification_result == "Needs Review":
        lead_stage = "manual_review"
        crm_status = "review_needed"
        booking_outcome = "not_ready"
        follow_up_action = "manual_review_required"
        review_required = True

    company_notified = (
        (qualification_result == "Qualified" and urgency == "High") or
        (qualification_result == "Suspicious")
    )

    result = {
        "lead_id": lead_id,
        "timestamp": timestamp,
        "source": source,
        "name": name,
        "phone": phone,
        "message": message,
        "timeline": timeline,
        "language": language,
        "is_valid": is_valid,
        "spam_flag": spam_flag,
        "spam_reason": spam_reason,
        "service_category": service_cat,
        "classification_confidence": conf,
        "classification_method": classification_method,
        "urgency": urgency,
        "qualification_result": qualification_result,
        "routing_decision": next_action,
        "booking_outcome": booking_outcome,
        "follow_up_action": follow_up_action,
        "crm_status": crm_status,
        "lead_stage": lead_stage,
        "lead_owner": lead_owner,
        "session_terminated": session_terminated,
        "block_recommended": block_recommended,
        "review_required": review_required,
        "company_notified": company_notified,
        "error_reason": err_reason
        
    }

    return result

def log_lead(result, filename="lead_log.csv"):
    fieldnames = [
        "lead_id",
        "timestamp",
        "source",
        "name",
        "phone",
        "message",
        "timeline",
        "language",
        "is_valid",
        "spam_flag",
        "spam_reason",
        "service_category",
        "classification_confidence",
        "classification_method",
        "urgency",
        "qualification_result",
        "routing_decision",
        "booking_outcome",
        "follow_up_action",
        "crm_status",
        "lead_stage",
        "lead_owner",
        "session_terminated",
        "block_recommended",
        "review_required",
        "company_notified",
        "error_reason"
    ]

    file_exists = os.path.isfile(filename)
    with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

if __name__ == "__main__":
    test_leads = [
        {
            "name": "John Doe",
            "phone": "555-1234",
            "message": "I have a leak in my kitchen sink. Can you fix it today?",
            "timeline": "today"
        },
        {
            "name": "",
            "phone": "555-5678",
            "message": "My AC is not cooling. Please help!",
            "timeline": "asap"
        },
        {
            "name": "Jane Smith",
            "phone": "",
            "message": "I need an electrician to install new outlets.",
            "timeline": "this week"
        },
        {
            "name": "Bob Johnson",
            "phone": "555-8765",
            "message": "",
            "timeline": ""
        },
        {
            "name": "Alice Brown",
            "phone": "555-4321",
            "message": "Free win prize click here!",
            "timeline": ""
        },
        {
            "name": "Carlos García",
            "phone": "555-0000",
            "message": "Necesito ayuda urgente con una fuga de agua en el baño. ¿Pueden venir hoy?",
            "timeline": "hoy"
        }
    ]

    for i, lead in enumerate(test_leads, start=1):
        print(f"\n--- Processing Lead {i} ---")
        result = process_lead(name=lead["name"], phone=lead["phone"], message=lead["message"], timeline=lead["timeline"], source="test_case")
        log_lead(result)
        for key, value in result.items():
            print(f"{key}: {value}")