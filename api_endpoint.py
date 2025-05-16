import streamlit as st
from groq import Groq
import os
import urllib.parse
# --- Configurazione Pagina Streamlit ---
st.set_page_config(
    page_title="Rielaboratore Testo Fumetto AI",
    page_icon="🗯️",
    layout="wide"
)
st.title("🗯️ Rielaboratore Testo Stile Fumetto AI 📝")
st.caption("Powered by Groq LLM")
# --- Accesso API Key ---
groq_api_key = None
try:
    # Prima prova dai segreti di Streamlit (per il deploy)
    groq_api_key = st.secrets.get("GROQ_API_KEY")
except Exception: # st.secrets non esiste localmente fuori da un contesto di app in esecuzione su Cloud
    pass
if not groq_api_key:
    # Poi prova dalle variabili d'ambiente (per esecuzione locale con .env)
    groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    st.error("Chiave API Groq (GROQ_API_KEY) non trovata! Assicurati di averla configurata nei segreti di Streamlit Cloud o nelle variabili d'ambiente locali.")
    st.stop()
client = Groq(api_key=groq_api_key)
# --- Funzione per chiamare Groq ---
def rielabora_testo_con_groq(testo_originale, modello_llm="llama3-8b-8192"):
    if not testo_originale or not testo_originale.strip():
        return "Nessun testo fornito per la rielaborazione."
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei un assistente AI che riscrive testi per adattarli allo stile di un fumetto o di una graphic novel. "
                        "Il tuo obiettivo è rendere il testo più vivace, dinamico e coinvolgente, come se fosse narrato in una vignetta. "
                        "Usa esclamazioni, onomatopee (come 'BOOM!', 'WHAM!', 'GASP!'), pensieri diretti ('Hmm, interessante...'), e brevi dialoghi immaginari se il contesto lo permette. "
                        "Spezza frasi lunghe. Enfatizza parole chiave. Non devi inventare storie nuove, ma trasformare lo stile del testo dato. "
                        "NON iniziare la tua risposta con frasi come 'Ecco il testo rielaborato:' o simili. Rispondi direttamente con il testo trasformato. "
                        "Mantieni il significato principale del testo originale. Sii creativo e divertente!"
                    )
                },
                {
                    "role": "user",
                    "content": f"Per favore, rielabora il seguente testo in uno stile da fumetto:\n\n---\n{testo_originale}\n---"
                }
            ],
            model=modello_llm,
            temperature=0.7,
            max_tokens=1500, # Aumentato per testi potenzialmente più lunghi
            top_p=1,
            stop=None,
            stream=False
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Errore durante la chiamata all'API Groq: {e}")
        return "Errore nella rielaborazione del testo."
# --- Interfaccia Utente ---
# Ottieni il testo dal parametro URL 'text'
query_params = st.query_params
testo_da_url_codificato = query_params.get("text", "")
testo_da_url_decodificato = ""
if testo_da_url_codificato:
    try:
        testo_da_url_decodificato = urllib.parse.unquote(testo_da_url_codificato)
    except Exception as e:
        st.warning(f"Impossibile decodificare il testo dall'URL: {e}")
st.subheader("Testo da Rielaborare:")
testo_input = st.text_area(
    "Inserisci o modifica il testo qui:",
    value=testo_da_url_decodificato,
    height=250,
    key="testo_originale_area"
)
col1, col2 = st.columns(2)
with col1:
    modello_selezionato = st.selectbox(
        "Scegli il modello Groq:",
        ("llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it", "llama3-70b-8192"),
        index=0,
        help="Scegli il modello LLM di Groq da usare per la rielaborazione."
    )
with col2:
    st.write("") 
    st.write("") 
    if st.button("✨ Rielabora in Stile Fumetto!", use_container_width=True, type="primary"):
        if testo_input and testo_input.strip():
            with st.spinner("Groq sta creando la magia... 🧠💭💥 POW!"):
                testo_rielaborato = rielabora_testo_con_groq(testo_input, modello_selezionato)
                st.session_state.testo_rielaborato = testo_rielaborato
        else:
            st.warning("Per favore, inserisci del testo da rielaborare.")
if "testo_rielaborato" in st.session_state:
    st.subheader("💬 Testo Rielaborato in Stile Fumetto:")
    # Usiamo st.markdown per una migliore visualizzazione e la possibilità di usare HTML/CSS in futuro se necessario
    container = st.container(border=True)
    container.markdown(st.session_state.testo_rielaborato)
st.markdown("---")
st.markdown("App creata come backend per l'estensione 'Converti Articolo in Fumetto'.")
