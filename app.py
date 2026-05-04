import streamlit as st
import google.generativeai as genai
import PyPDF2

# Configurare Pagina
st.set_page_config(page_title="MedQuiz AI - Grile Automate", layout="centered")
st.title("🩺 MedQuiz AI")
st.subheader("Transformă cursurile în grile de medicină")

# --- CONFIGURARE API KEY DIN SECRETS ---
try:
    # Citim cheia din sistemul de secrete al Streamlit
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_configured = True
except Exception:
    st.error("⚠️ Eroare: Cheia API nu a fost găsită în 'Streamlit Secrets'.")
    st.info("Dacă rulezi local, adaugă cheia în .streamlit/secrets.toml. Dacă ești pe Cloud, adaugă GEMINI_API_KEY în setările aplicației.")
    api_configured = False

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Interfața de încărcare
uploaded_file = st.file_uploader("Încarcă cursul de medicină (PDF)", type="pdf")
num_questions = st.slider("Câte grile dorești să generezi?", 5, 20, 10)

if st.button("Generează Grile ✨") and uploaded_file and api_configured:
    with st.spinner("Gemini analizează textul și creează întrebările..."):
        context = extract_text_from_pdf(uploaded_file)
        
        # Prompt optimizat pentru acuratețe medicală
        prompt = f"""
        Ești un profesor universitar expert în medicină. Bazându-te EXCLUSIV pe textul furnizat mai jos, generează {num_questions} grile.
        
        Cerințe:
        1. Mix de întrebări: Complement Simplu și Complement Multiplu.
        2. Format: Întrebare, urmată de variantele A, B, C, D, E.
        3. Răspunsul corect indicat clar la finalul fiecărei întrebări.
        4. EXPLICAȚIE: Oferă o scurtă explicație pentru răspunsul corect, citând informația din text.

        Text: {context[:15000]}  # Procesăm primele 15k caractere pentru context extins
        
        Format output: Markdown curat.
        """
        
        try:
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown(response.text)
            
            # Opțiune de download
            st.download_button(
                label="Descarcă Grilele (TXT)",
                data=response.text,
                file_name="grile_medicina_generate.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"A apărut o eroare la generare: {e}")

elif not uploaded_file:
    st.info("Încarcă un fișier PDF pentru a începe generarea.")
