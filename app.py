# app.py (Modified for Manual Loading)
import gradio as gr
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch # Переконайся, що torch є в requirements.txt

MODEL_NAME = "benjamin/gpt2-wechsel-ukrainian"
model = None
tokenizer = None
# Визначаємо, чи є на Space доступ до GPU (графічного процесора), чи використовувати звичайний (CPU)
# На безкоштовних планах зазвичай тільки CPU
device = "cuda" if torch.cuda.is_available() else "cpu" 

print(f"Використовується пристрій: {device}")

try:
    print(f"Завантаження токенізатора: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    print("Токенізатор завантажено.")

    print(f"Завантаження моделі: {MODEL_NAME}")
    # Завантажуємо саму модель і переміщуємо її на визначений пристрій (CPU або GPU)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(device) 
    print("Модель завантажено успішно.")

except Exception as e:
    # Якщо на якомусь етапі виникла помилка, виводимо її
    print(f"Помилка під час завантаження моделі або токенізатора: {e}")
    # Залишаємо model і tokenizer як None, щоб бачити помилку в інтерфейсі пізніше

def get_bot_response(user_message):
    # Перевіряємо, чи вдалося завантажити модель і токенізатор раніше
    if model is None or tokenizer is None:
        return "Вибачте, модель AI або токенізатор не завантажилися на сервері. Перевірте код і логи на Hugging Face Space."

    try:
        print(f"Отримано повідомлення: {user_message}")
        # 1. Перетворюємо текст користувача на числа, зрозумілі моделі (токенізація)
        # і відправляємо ці дані на той же пристрій (CPU/GPU), де знаходиться модель
        inputs = tokenizer.encode(user_message, return_tensors="pt").to(device) 

        print("Генерація відповіді...")
        # 2. Віддаємо ці числа моделі, щоб вона згенерувала продовження (відповідь)
        # Параметри генерації можна налаштовувати (довжина, уникнення повторів тощо)
        outputs = model.generate(
            inputs,
            max_length=100, # Максимальна довжина відповіді у токенах (приблизно слова/частини слів)
            num_return_sequences=1, # Хочемо отримати одну відповідь
            pad_token_id=tokenizer.eos_token_id, # Важливо, щоб уникнути попереджень
            no_repeat_ngram_size=2, # Щоб зменшити повторення фраз з 2 слів
            early_stopping=True # Зупинити генерацію раніше, якщо модель вважає речення завершеним
        )
        print("Генерація завершена.")

        # 3. Перетворюємо числа-відповідь назад у звичайний текст
        bot_response_full = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Повна відповідь моделі: {bot_response_full}")

        # 4. Часто модель повторює вхідне повідомлення на початку відповіді. Спробуємо його видалити.
        # Ця логіка може потребувати покращення для деяких випадків.
        bot_response_cleaned = bot_response_full.replace(user_message, "").strip()
        
        # Якщо після видалення нічого не лишилось (наприклад, модель відповіла тим самим), 
        # то повертаємо повну відповідь, як вона є.
        bot_response = bot_response_cleaned if bot_response_cleaned else bot_response_full

        print(f"Відповідь для користувача: {bot_response}")
        return bot_response

    except Exception as e:
        # Якщо під час генерації сталася помилка
        print(f"Помилка під час генерації: {e}")
        return f"Виникла помилка під час генерації відповіді: {e}"

# Створюємо інтерфейс Gradio (ця частина залишається майже без змін)
iface = gr.Interface(
    fn=get_bot_response, # Функція, яка буде викликатись для отримання відповіді
    inputs=gr.Textbox(lines=2, placeholder="Введіть ваше повідомлення тут..."), # Поле для вводу тексту
    outputs=gr.Textbox(), # Поле для виводу відповіді
    title="Мій Український Чат-Бот v0.0.2 (Manual Load)", # Назва вікна
    description="Простий чат-бот на базі моделі з Hugging Face (benjamin/gpt2-wechsel-ukrainian)."
)

# Запускаємо веб-сервер Gradio
iface.launch()