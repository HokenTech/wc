import streamlit as st
import json
import requests
import os

# Costanti per chiamare l'API Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
REQUEST_TIMEOUT = 90  # timeout in secondi

def transform_text_narrative(api_key: str, text: str) -> str:
    """
    Chiama l'API Groq per elaborare il testo.
    Costruisce un prompt per la trasformazione in stile fumettistico, invia la richiesta 
    in formato JSON e restituisce il testo processato.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
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
        # Restituisce il contenuto elaborato, rimuovendo spazi iniziali/finali
        return message.get("content", "").strip()
    return ""

def main():
    # Recupera la chiave API Groq dalle variabili di ambiente o dai secrets di Streamlit
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY non configurata.")
        return

    # Utilizza st.query_params per verificare la presenza del parametro 'api'
    params = st.query_params
    if "api" in params:
        # Recupera il parametro 'text' dalla query string
        input_text = params.get("text", [""])[0]
        if not input_text:
            st.error("Parametro 'text' mancante.")
            return

        try:
            # Chiama la funzione di trasformazione del testo tramite API Groq
            processed_text = transform_text_narrative(api_key, input_text)
            response_data = {"processedText": processed_text}
            # Restituisce la risposta in formato JSON
            st.write(json.dumps(response_data))
        except Exception as e:
            st.error(f"Errore durante la trasformazione: {e}")
    else:
        st.write("Questo endpoint è destinato alle chiamate API. Passa il parametro ?api=1 nella query string.")

if __name__ == "__main__":
    main()
