import streamlit as st
from openai import OpenAI, OpenAIError
import fitz  # PyMuPDF
from docx import Document

# Налаштування API-ключа OpenAI з Streamlit secrets
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("Відсутній ключ OpenAI API. Будь ласка, додайте його у файл secrets.toml.")
    st.stop()
except Exception as e:
    st.error(f"Помилка при ініціалізації клієнта OpenAI: {e}")
    st.stop()

# --- Функція для вилучення тексту з файлів ---
def extract_text_from_file(uploaded_file):
    """
    Витягує текст з завантаженого файлу (PDF, DOCX, TXT).
    """
    file_type = uploaded_file.type
    text = ""
    try:
        if file_type == "application/pdf":
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        elif file_type == "text/plain":
            text = uploaded_file.getvalue().decode("utf-8")
        else:
            st.error(f"Непідтримуваний тип файлу: {file_type}")
    except Exception as e:
        st.error(f"Помилка при читанні файлу: {e}")
    return text

# --- Функція для виклику API OpenAI ---
def call_openai_api(prompt):
    """
    Викликає OpenAI API для генерації контенту.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти — професійний асистент, що спеціалізується на аналізі вакансій та резюме."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        st.error(f"Сталася помилка при зверненні до OpenAI API: {e}")
        return None

# --- Налаштування сторінки ---
st.set_page_config(page_title="AI Асистент для Вакансій", layout="wide")
st.title("AI Асистент для аналізу вакансій")
st.subheader("Миттєво оптимізуйте своє резюме під конкретну вакансію.")

# --- Розділяємо інтерфейс на вкладки ---
tab_resume, tab_cover_letter, tab_interview, tab_skills = st.tabs([
    "📝 Аналіз резюме",
    "✉️ Створити супровідний лист",
    "❓ Підготовка до співбесіди",
    "🎯 Сильні сторони"
])

# --- Логіка для вкладки "Аналіз резюме" ---
with tab_resume:
    st.info("Вставте текст вакансії та завантажте резюме. AI проаналізує їх і надасть рекомендації.")
    job_posting = st.text_area("📄 **Вставте текст вакансії:**", height=250, help="Скопіюйте опис вакансії повністю.", key="job_resume")
    
    st.markdown("---")
    resume_file = st.file_uploader("📝 **Або завантажте ваше резюме:**", type=["pdf", "docx", "txt"], help="Завантажте резюме у форматі PDF, DOCX або TXT.", key="resume_file_resume_tab")
    
    analyze_button = st.button("🚀 Аналізувати та підготувати резюме")

    if analyze_button:
        if not job_posting or