import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document

# Налаштування API-ключа з Streamlit secrets
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("Відсутній ключ Google Gemini API. Будь ласка, додайте його у файл secrets.toml.")
    st.stop()

# Ініціалізація моделі
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="AI Асистент для Вакансій", layout="wide")

st.title("AI Асистент для аналізу вакансій")
st.subheader("Миттєво оптимізуйте своє резюме під конкретну вакансію.")

# --- Функція для вилучення тексту з файлів ---
def extract_text_from_file(file_path, file_type):
    """
    Витягує текст з завантаженого файлу (PDF, DOCX, TXT).
    """
    text = ""
    if file_type == "application/pdf":
        try:
            pdf_document = fitz.open(stream=file_path.read(), filetype="pdf")
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
        except Exception as e:
            st.error(f"Помилка при читанні PDF: {e}")
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            st.error(f"Помилка при читанні DOCX: {e}")
    elif file_type == "text/plain":
        try:
            text = file_path.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Помилка при читанні TXT: {e}")
    return text

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
        if not job_posting:
            st.warning("Будь ласка, заповніть поле вакансії.")
        elif not resume_file:
            st.warning("Будь ласка, завантажте файл резюме.")
        else:
            user_resume = extract_text_from_file(resume_file, resume_file.type)
            if not user_resume:
                st.error("Не вдалося витягти текст з файлу. Перевірте формат або спробуйте вставити текст вручну.")
            else:
                prompt = f"""
                ... ваш промпт для аналізу резюме ...
                """
                with st.spinner("🧠 AI аналізує..."):
                    try:
                        response = model.generate_content(prompt.replace("{job_posting}", job_posting).replace("{user_resume}", user_resume))
                        st.success("✅ Аналіз завершено!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Сталася помилка при зверненні до AI: {e}")

# --- Логіка для вкладки "Створити супровідний лист" ---
with tab_cover_letter:
    st.info("Вставте текст вакансії та назву компанії, а потім завантажте резюме. AI згенерує персоналізований супровідний лист.")
    
    company_name = st.text_input("🏢 **Назва компанії:**", key="company_name_cl")
    job_posting_cl = st.text_area("📄 **Вставте текст вакансії:**", height=200, key="job_cl")
    
    st.markdown("---")
    resume_file_cl = st.file_uploader("📝 **Або завантажте ваше резюме:**", type=["pdf", "docx", "txt"], key="resume_file_cl_tab")
    
    generate_cl_button = st.button("✍️ Створити супровідний лист")

    if generate_cl_button:
        if not job_posting_cl or not resume_file_cl or not company_name:
            st.warning("Будь ласка, заповніть усі поля.")
        else:
            user_resume_cl = extract_text_from_file(resume_file_cl, resume_file_cl.type)
            if not user_resume_cl:
                 st.error("Не вдалося витягти текст з файлу.")
            else:
                cl_prompt = f"""
                ... ваш промпт для супровідного листа ...
                """
                with st.spinner("🧠 AI створює лист..."):
                    try:
                        cl_response = model.generate_content(cl_prompt.replace("{company_name}", company_name).replace("{job_posting_cl}", job_posting_cl).replace("{user_resume_cl}", user_resume_cl))
                        st.success("✅ Лист готовий!")
                        st.markdown(cl_response.text)
                    except Exception as e:
                        st.error(f"Сталася помилка при зверненні до AI: {e}")

# --- Логіка для вкладки "Підготовка до співбесіди" ---
with tab_interview:
    st.markdown("### ❓ Підготовка до співбесіди")
    st.info("Вставте текст вакансії та завантажте резюме. AI згенерує список питань, які можуть поставити на співбесіді.")
    
    job_posting_int = st.text_area("📄 **Вставте текст вакансії:**", height=200, key="job_interview")
    
    st.markdown("---")
    resume_file_int = st.file_uploader("📝 **Або завантажте ваше резюме:**", type=["pdf", "docx", "txt"], key="resume_file_int_tab")
    
    interview_button = st.button("❓ Згенерувати питання для співбесіди")
    
    if interview_button:
        if not job_posting_int or not resume_file_int:
            st.warning("Будь ласка, заповніть обидва поля.")
        else:
            user_resume_int = extract_text_from_file(resume_file_int, resume_file_int.type)
            if not user_resume_int:
                st.error("Не вдалося витягти текст з файлу.")
            else:
                interview_prompt = f"""
                ... ваш промпт для питань на співбесіду ...
                """
                with st.spinner("🧠 AI готує питання..."):
                    try:
                        interview_response = model.generate_content(interview_prompt.replace("{job_posting_int}", job_posting_int).replace("{user_resume_int}", user_resume_int))
                        st.success("✅ Питання готові!")
                        st.markdown(interview_response.text)
                    except Exception as e:
                        st.error(f"Сталася помилка при зверненні до AI: {e}")

# --- Логіка для вкладки "Аналіз сильних сторін" ---
with tab_skills:
    st.markdown("### 🎯 Аналіз сильних сторін")
    st.info("Завантажте ваше резюме, і AI проаналізує його, щоб виділити ваші ключові сильні сторони.")

    resume_file_skills = st.file_uploader("📝 **Завантажте ваше резюме:**", type=["pdf", "docx", "txt"], key="resume_file_skills_tab")
    
    skills_button = st.button("🔍 Визначити сильні сторони")
    
    if skills_button:
        if not resume_file_skills:
            st.warning("Будь ласка, завантажте файл резюме.")
        else:
            user_resume_skills = extract_text_from_file(resume_file_skills, resume_file_skills.type)
            if not user_resume_skills:
                st.error("Не вдалося витягти текст з файлу.")
            else:
                skills_prompt = f"""
                ... ваш промпт для аналізу сильних сторін ...
                """
                with st.spinner("🧠 AI аналізує..."):
                    try:
                        skills_response = model.generate_content(skills_prompt.replace("{user_resume_skills}", user_resume_skills))
                        st.success("✅ Аналіз завершено!")
                        st.markdown(skills_response.text)
                    except Exception as e:
                        st.error(f"Сталася помилка при зверненні до AI: {e}")