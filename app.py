# app.py 0.1.0
import gradio as gr
from transformers import pipeline

# Завантаження моделі та токенізатора
try:
    generator = pipeline('text-generation', model='benjamin/gpt2-wechsel-ukrainian')
    print("Модель та токенізатор завантажено успішно.")
except Exception as e:
    print(f"Помилка під час завантаження моделі або токенізатора: {e}")
    # Обробка помилки: можна використати іншу модель, вивести повідомлення користувачу, або завершити роботу
    exit()  # Завершення роботи скрипта при помилці завантаження

def get_bot_response(user_message):
    """
    Генерує відповідь бота на повідомлення користувача.
    """

    # Обробка вхідних даних
    print(f"Отримано повідомлення від користувача: {user_message}")

    # Перевірка на команди (приклад)
    if user_message.startswith("/переклад"):
        # Виклик функції перекладу (потрібно реалізувати)
        bot_response = "Функція перекладу ще не реалізована."
    elif user_message.startswith("/код"):
        # Виклик функції генерації коду (потрібно реалізувати)
        bot_response = "Функція генерації коду ще не реалізована."
    else:
        try:
            # Генеруємо відповідь за допомогою моделі
            bot_response_full = generator(user_message, max_length=200)[0]['generated_text']

            # Видаляємо вхідне повідомлення на початку відповіді.
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
    fn=get_bot_response,  # Функція, яка буде викликатись для отримання відповіді
    inputs=gr.Textbox(lines=2, placeholder="Введіть ваше повідомлення тут..."),  # Поле для вводу тексту
    outputs=gr.Textbox(),  # Поле для виводу відповіді
    title="Чат для чатботів v0.1.0",  # Змінено назву
    description="Простий чат-бот на базі моделі з Hugging Face (benjamin/gpt2-wechsel-ukrainian)"  # Опис
)

if __name__ == '__main__':
    iface.launch()