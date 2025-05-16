import streamlit as st
import json
import requests
import os
import re

# Costanti per chiamare l'API Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
REQUEST_TIMEOUT = 90  # timeout in secondi

def transform_text_narrative(api_key: str, text: str) -> str:
    """Chiama l'API Groq per elaborare il testo."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    # Il prompt include istruzioni per ottenere titoli per ciascun pannello
    prompt = (
        "Riscrivi il seguente testo in uno stile fumettistico narrativo "
        "con titoli espliciti per ogni paragrafo. Non inserire la sequenza '\\n\\n' "
        "ma usa interruzioni di linea naturali per separare i pannelli.\n\n" + text
    )
    payload = {
        "model": GROQ_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 3500,
    }
    response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices", [])
    if choices and isinstance(choices, list) and len(choices) > 0:
        message = choices[0].get("message", {})
        return message.get("content", "").strip()
    return ""

def main():
    # Configura la chiave API Groq (da impostare nelle variabili di ambiente o in secrets)
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY non configurata.")
        return

    # Controlla se la richiesta è intesa per l'endpoint API, ad es. ?api=1&text=...
    params = st.experimental_get_query_params()
    if "api" in params:
        # Recupera il parametro 'text'
        input_text = params.get("text", [""])[0]
        if not input_text:
            st.error("Parametro 'text' mancante.")
            return
        try:
            processed_text = transform_text_narrative(api_key, input_text)
            response_data = {"processedText": processed_text}
            st.write(json.dumps(response_data))
        except Exception as e:
            st.error(f"Errore durante la trasformazione: {e}")
    else:
        st.write("Questo endpoint è destinato alle chiamate API. Passa il parametro ?api=1 nella query string.")

if __name__ == "__main__":
    main()
