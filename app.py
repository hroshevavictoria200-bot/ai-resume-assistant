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
        if not job_posting or not resume_file:
            st.warning("Будь ласка, заповніть обидва поля.")
        else:
            user_resume = extract_text_from_file(resume_file)
            if not user_resume:
                st.error("Не вдалося витягти текст з файлу. Будь ласка, спробуйте інший файл.")
            else:
                prompt = f"""
                Ти — AI-асистент, що спеціалізується на аналізі вакансій та підготовці резюме.
                Твоє завдання — надати користувачу структурований та корисний аналіз.

                **Крок 1: Аналіз Вакансії**
                Виділи ключові вимоги, необхідні навички, досвід та технології, перелічені у вакансії.

                **Крок 2: Порівняння з Резюме**
                Порівняй навички та досвід, зазначені у наданому резюме, з вимогами вакансії.

                **Крок 3: Формування Рекомендацій**
                На основі аналізу, створи три розділи:
                
                ### 🟢 Відповідності в резюме
                * Перелічи навички та досвід із резюме, які безпосередньо збігаються з вимогами вакансії. Використовуй списки.

                ### 🔴 Прогалини в навичках
                * Перелічи навички, які вказані у вакансії, але відсутні в резюме. Використовуй списки.

                ### 📝 Рекомендації щодо редагування резюме
                * Запропонуй, як переписати або доповнити резюме, щоб воно краще відповідало вакансії.
                * Вкажи, які ключові слова з вакансії варто додати.
                * Запропонуй, як можна переформулювати досвід, щоб він звучав більш релевантно.

                ---

                **ВАКАНСІЯ:**
                {job_posting}

                **РЕЗЮМЕ:**
                {user_resume}
                """
                with st.spinner("🧠 AI аналізує..."):
                    response_text = call_openai_api(prompt)
                    if response_text:
                        st