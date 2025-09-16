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
                        st.success("✅ Аналіз завершено!")
                        st.markdown(response_text)

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
            user_resume_cl = extract_text_from_file(resume_file_cl)
            if not user_resume_cl:
                 st.error("Не вдалося витягти текст з файлу.")
            else:
                cl_prompt = f"""
                Ти — професійний асистент для написання супровідних листів.
                Твоє завдання — написати переконливий супровідний лист, який ідеально підходить для вакансії, враховуючи навички та досвід кандидата.

                **Інструкції:**
                1.  Звертайся до компанії по імені: {company_name}.
                2.  Виділи 2-3 ключові навички з резюме, які найкраще відповідають вимогам вакансії.
                3.  Поясни, як досвід кандидата (з резюме) дозволяє йому успішно виконувати обов'язки, зазначені у вакансії.
                4.  Лист має бути професійним, лаконічним і переконливим.

                ---

                **ВАКАНСІЯ:**
                {job_posting_cl}

                **РЕЗЮМЕ:**
                {user_resume_cl}
                """
                with st.spinner("🧠 AI створює лист..."):
                    response_text = call_openai_api(cl_prompt)
                    if response_text:
                        st.success("✅ Лист готовий!")
                        st.markdown(response_text)

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
            user_resume_int = extract_text_from_file(resume_file_int)
            if not user_resume_int:
                st.error("Не вдалося витягти текст з файлу.")
            else:
                interview_prompt = f"""
                Ти — досвідчений HR-менеджер. Твоє завдання — згенерувати список потенційних питань для співбесіди, 
                виходячи з наданої вакансії та резюме кандидата.

                **Інструкції:**
                1.  Сформулюй від 5 до 10 питань.
                2.  Включи технічні питання, що стосуються ключових навичок з вакансії.
                3.  Додай поведінкові питання (наприклад, "Розкажіть про ситуацію, коли...").
                4.  Запропонуй питання, що перевіряють мотивацію кандидата та його зацікавленість у компанії.
                5.  Використовуй списки для зручності читання.

                ---
                
                **ВАКАНСІЯ:**
                {job_posting_int}

                **РЕЗЮМЕ:**
                {user_resume_int}
                """
                with st.spinner("🧠 AI готує питання..."):
                    response_text = call_openai_api(interview_prompt)
                    if response_text:
                        st.success("✅ Питання готові!")
                        st.markdown(response_text)

# --- Логіка для вкладки "Аналіз сильних сторін" ---
with tab_skills:
    st.markdown("### 🎯 Аналіз сильних сторін")
    st.info("Завантажте ваше резюме, і AI проаналізує його, щоб виділити ваші ключові сильні сторони.")
    resume_file_skills = st.file_uploader("📝 **Завантажте ваше резюме:**", type=["pdf", "docx", "txt"], key="resume_file_skills_tab")
    
    skills_button = st.button("🔍 Визначити сильні сторони")
    
    if skills_button:
        if not resume_file_skills:
            st.warning("Будь ласка, заповніть файл резюме.")
        else:
            user_resume_skills = extract_text_from_file(resume_file_skills)
            if not user_resume_skills:
                st.error("Не вдалося витягти текст з файлу.")
            else:
                skills_prompt = f"""
                Ти — кар'єрний консультант. Твоє завдання — проаналізувати резюме кандидата і виділити його ключові сильні сторони, 
                виходячи з досвіду та навичок.

                **Інструкції:**
                1.  Виділи 3-5 найважливіших сильних сторін.
                2.  Для кожної сильної сторони наведи 1-2 приклади з резюме, які її підтверджують.
                3.  Поясни, чому ці сильні сторони є цінними для потенційного роботодавця.
                4.  Використовуй марковані списки.

                ---
                
                **РЕЗЮМЕ:**
                {user_resume_skills}
                """
                with st.spinner("🧠 AI аналізує..."):
                    response_text = call_openai_api(skills_prompt)
                    if response_text:
                        st.success("✅ Аналіз завершено!")
                        st.markdown(response_text)