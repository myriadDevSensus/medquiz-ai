import streamlit as st
import google.generativeai as genai
import PyPDF2

st.set_page_config(page_title="MedQuiz AI", layout="centered")
st.title("🩺 MedQuiz AI")

# --- API SETUP ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# DEBUG: Let's find out what models your key can actually see
def get_available_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prefer 1.5 Flash, then 1.5 Flash-latest, then 1.0 Pro
        if 'models/gemini-1.5-flash' in models:
            return 'gemini-1.5-flash'
        elif 'models/gemini-1.5-flash-latest' in models:
            return 'gemini-1.5-flash-latest'
        elif 'models/gemini-pro' in models:
            return 'gemini-pro'
        return models[0] if models else None
    except Exception as e:
        st.error(f"Error listing models: {e}")
        return "gemini-1.5-flash" # Fallback

model_id = get_available_model()
model = genai.GenerativeModel(model_id)

st.info(f"Using model: {model_id}")

# --- APP LOGIC ---
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

uploaded_file = st.file_uploader("Încarcă cursul (PDF)", type="pdf")
num_questions = st.slider("Număr grile", 5, 20, 10)

if st.button("Generează Grile ✨") and uploaded_file:
    with st.spinner("Generăm..."):
        context = extract_text_from_pdf(uploaded_file)
        
        prompt = f"Ești profesor de medicină. Generază {num_questions} grile din acest text: {context[:15000]}"
        
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Eroare la generare: {e}")
