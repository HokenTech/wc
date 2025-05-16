import streamlit as st
import os
import json
from groq import Groq

# Configura la pagina Streamlit (opzionale, ma buono per dare un titolo)
st.set_page_config(page_title="Servizio Rielaborazione Testo Fumetto", layout="centered")

# Recupera la chiave API di Groq dai segreti di Streamlit
# Assicurati di aver configurato un segreto chiamato 'GROQ_API_KEY' in Streamlit Cloud
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Errore nell'inizializzazione del client Groq: Assicurati che GROQ_API_KEY sia configurata nei segreti di Streamlit. Dettagli: {e}")
    st.stop()

def rielabora_testo_con_groq(testo_originale):
    if not testo_originale or not testo_originale.strip():
        return ""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei un assistente creativo specializzato nella scrittura di fumetti. "
                        "Il tuo compito è rielaborare il testo fornito per renderlo più vivace, conciso e adatto "
                        "allo stile di un dialogo o una narrazione da fumetto. "
                        "Usa un linguaggio colorito, diretto, e se appropriato, onomatopee o esclamazioni tipiche dei fumetti. "
                        "Mantieni il significato originale del testo."
                        "NON includere prefissi come 'Testo rielaborato:' o simili nella tua risposta. Fornisci solo il testo trasformato."
                        "Rispondi in italiano."
                    )
                },
                {
                    "role": "user",
                    "content": f"Rielabora il seguente testo per un fumetto: \"{testo_originale}\"",
                }
            ],
            model="llama3-70b-8192", # Puoi scegliere un altro modello Groq se preferisci
            temperature=0.7,
            max_tokens=len(testo_originale.split()) * 3 + 50, # Stima approssimativa per output più lungo
            top_p=0.9,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Errore durante la chiamata all'API Groq: {e}")
        return testo_originale # Restituisce l'originale in caso di errore

# Questo è il "cuore" del nostro finto endpoint API
# Legge il testo dai parametri query dell'URL
query_params = st.query_params.to_dict()
testo_da_rielaborare = query_params.get("text_to_rephrase", [None])[0]

risultato_rielaborato = ""

if testo_da_rielaborare:
    #st.write(f"Testo originale ricevuto: {testo_da_rielaborare}") # Debug
    with st.spinner("🤖 Un attimo, il nostro sceneggiatore AI è all'opera..."):
        risultato_rielaborato = rielabora_testo_con_groq(testo_da_rielaborare)
    
    # Mostra il risultato nell'UI di Streamlit (utile per testare direttamente l'app)
    # st.subheader("Testo Rielaborato dal AI:")
    # st.markdown(f"> {risultato_rielaborato}") # Lo commentiamo per non ingombrare se usato come API
else:
    st.info("Benvenuto! Questo servizio rielabora il testo per fumetti. Funziona tramite parametri URL.")

# Prepara i dati di risposta JSON da inserire in un div nascosto per il plugin
response_payload = {
    "original_text": testo_da_rielaborare if testo_da_rielaborare else "",
    "rephrased_text": risultato_rielaborato
}

# Inserisce i dati JSON in un div nascosto che il plugin può leggere.
# Usiamo st.markdown perché st.json() crea una visualizzazione UI complessa.
# Questo è il modo per far sì che il plugin prenda i dati.
st.markdown(f"""
<div id="api-response-data" style="display:none;">
{json.dumps(response_payload)}
</div>
""", unsafe_allow_html=True)

# Opzionale: un piccolo footer o info
st.markdown("---")
st.caption("Servizio di Rielaborazione Testo per Plugin Fumetto v1.0")

# Per testare l'app direttamente, puoi aggiungere un input utente:
st.sidebar.header("Test Manuale")
test_text_manual = st.sidebar.text_area("Incolla qui il testo da rielaborare per un test:", height=100)
if st.sidebar.button("Rielabora Testo (Test Manuale)"):
    if test_text_manual:
        rephrased_for_manual_test = rielabora_testo_con_groq(test_text_manual)
        st.sidebar.subheader("Risultato Test Manuale:")
        st.sidebar.markdown(f"> {rephrased_for_manual_test}")
    else:
        st.sidebar.warning("Inserisci del testo per il test.")
