
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
    Chiama l'API Groq per elaborare il testo e restituire il contenuto trasformato.
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
        return message.get("content", "").strip()
    return ""

def generate_html_comic_layout(text: str) -> str:
    """
    Genera una pagina HTML con layout a fumetto a partire dal testo processato.
    Divide il testo in pannelli (usando le interruzioni doppie di linea) e formatta ciascun pannello.
    """
    panels = [p.strip() for p in text.split("\n\n") if p.strip()]
    panel_html_list = []
    for panel in panels:
        lines = panel.split("\n")
        title = lines[0].strip() if lines else "Titolo non specificato"
        # Unisce le restanti righe per costituire il contenuto, separandole con <br>
        content = "<br>".join(line.strip() for line in lines[1:]) if len(lines) > 1 else ""
        panel_html = f"""
          <div class="panel">
              <div class="panel-content">
                  <h2>{title}</h2>
                  <p>{content}</p>
              </div>
          </div>
        """
        panel_html_list.append(panel_html)
    all_panels = "\n".join(panel_html_list)
    html_page = f"""
    <html>
      <head>
         <meta charset="utf-8">
         <title>Comic Layout</title>
         <link href="https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap" rel="stylesheet">
         <style>
            body {{
                font-family: 'Comic Neue', cursive;
                background: linear-gradient(135deg, #f6f8fa, #e9ecef);
                margin: 0;
                padding: 20px;
                color: #24292e;
            }}
            .comic-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 25px;
                justify-content: center;
                max-width: 1400px;
                margin: 20px auto;
                padding: 25px;
                background-color: #ffffff;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }}
            .panel {{
                background: #ffffff;
                border: 4px solid #333;
                box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
                padding: 20px;
                border-radius: 8px;
                width: calc(50% - 25px);
                min-width: 320px;
            }}
            .panel h2 {{
                font-family: 'Bangers', cursive;
                color: #e53935;
                text-align: center;
                margin-top: 0;
                text-shadow: 1px 1px #555;
                font-size: 2.2em;
                margin-bottom: 15px;
            }}
            .panel p {{
                text-align: justify;
                line-height: 1.6;
                white-space: pre-wrap;
                font-size: 1.1em;
            }}
         </style>
      </head>
      <body>
         <div class="comic-container">
            {all_panels}
         </div>
      </body>
    </html>
    """
    return html_page

def main():
    # Recupera la chiave API Groq dalle variabili di ambiente o dai secrets
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        st.error("GROQ_API_KEY non configurata.")
        return

    params = st.query_params
    # Controlla se è stato fornito il parametro 'text'
    if "text" in params:
        input_text = params.get("text", [""])[0]
        if not input_text:
            st.error("Parametro 'text' mancante.")
            return

        try:
            processed_text = transform_text_narrative(api_key, input_text)
            # Se il parametro ?api=1 è presente, restituisce JSON
            if "api" in params:
                response_data = {"processedText": processed_text}
                st.write(json.dumps(response_data))
            else:
                # Altrimenti, restituisce una pagina HTML completa con layout a fumetto
                html_output = generate_html_comic_layout(processed_text)
                st.markdown(html_output, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Errore durante la trasformazione: {e}")
    else:
        st.write("Utilizza il parametro 'text' nella query string per inviare il testo da trasformare.")

if __name__ == "__main__":
    main()

