import os
from io import BytesIO
from google.genai import types

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

st.set_page_config(page_title="AI Fasting Recipe Assistant", page_icon="🥣", layout="centered")
st.title("🥣 AI Fasting Recipe Assistant")
st.caption("Завантажте фото продуктів, оберіть умови посту та отримайте рецепт.")

FASTING_MODES = {
    "Без м’яса": "не використовуй м’ясо та м’ясні продукти",
    "Без м’яса і молочного": "не використовуй м’ясо, рибу, молочні продукти",
    "Суворий піст": "не використовуй м’ясо, рибу, молочні продукти та яйця",
}

mode = st.selectbox("Умови посту", list(FASTING_MODES))
servings = st.slider("Кількість порцій", 1, 6, 2)
uploaded = st.file_uploader("Фото продуктів", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(BytesIO(uploaded.getvalue())).convert("RGB")
    image.thumbnail((1280, 1280))

    st.image(
        image,
        caption="Завантажені продукти",
        use_container_width=True
    )

    if st.button("Що приготувати?", type="primary", use_container_width=True):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("Не знайдено GEMINI_API_KEY. Додайте ключ у файл .env.")
            st.stop()

        prompt = f"""
Ти помічник з підбору рецептів. Проаналізуй фото продуктів.
Умова: {FASTING_MODES[mode]}.
Кількість порцій: {servings}.

Відповідай українською у структурі:
1. Розпізнані продукти.
2. Продукти на фото, що не відповідають обраній умові посту (якщо є).
3. Три варіанти страв.
4. Найкращий варіант: назва, час, інгредієнти та покроковий рецепт.
5. Що потрібно докупити.

Не вигадуй, що продукт точно є на фото, якщо не можеш упевнено його розпізнати.
Не давай медичних або богословських порад. Умову посту трактуй лише як харчове обмеження.
"""
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("Аналізую фото та складаю рецепт..."):
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
                    contents=[prompt, image],
                    config=types.GenerateContentConfig(
                        max_output_tokens=1200,
                        thinking_config=types.ThinkingConfig(
                            thinking_level=types.ThinkingLevel.LOW
                        ),
                    ),
                )
            st.subheader("Результат")
            st.markdown(response.text)
        except Exception as exc:
            st.error(f"Помилка API: {exc}")
else:
    st.info("Завантажте фотографію продуктів у форматі JPG або PNG.")
