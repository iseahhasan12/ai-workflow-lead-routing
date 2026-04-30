# AI Workflow for Lead Processing

## Overview
This system is designed to simulate an AI-driven workflow to process, classify, and route service requests to improve operational efficiency. The main goal was to explore how AI can be used in real-world workflows to automate decision-making and improve customer service.

## Key Features
- Validates user input and detects missing information
- Identifies spam messages
- Detects input language (English or Spanish)
- Classifies service requests (Plumbing, HVAC, Electrical, etc.)
- Routes requests to appropriate next steps (booking, review, follow-up)
- Logs results for tracking and analysis

## Tech Stack
- Python
- Pandas
- scikit-learn
- Streamlit

## How It Works
1. User submits a service request
2. System validates input and verifies spam
3. Request is classified using rules-based logic or a machine learning model (Logistic Regression and TfidVectorizer (TF-IDF))
4. Urgency is determined
5. System decides on how the request will be routed (booking, manual review, etc.)
6. Results are logged and displayed

## Example Output
```json
{
  "service_category":"Plumbing",
  "classification_method":"ml",
  "urgency":"High",
  "qualification_result":"Qualified",
  "routing_decision":"priority_follow_up"
}
```

## Why this Project Matters
This project demonstrates how AI can go beyond predictions and be used to automate repetitive real-world workflows. It also reflects how businesses can improve operational efficiency and in turn, enhance customer experience.

## Future Improvements
- Integrate LLMs for more flexible and intelligent request understanding
- Improve classification accuracy with larger datasets
- Connect to real APIs for booking and CRM systems
- Implement a more advanced AI agent for request handling and processing
