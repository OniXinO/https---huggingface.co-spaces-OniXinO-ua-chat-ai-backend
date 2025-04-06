# desktop_client/desktop_client.py 0.0.5
import tkinter as tk
from tkinter import scrolledtext
import requests
import threading  # Для асинхронного оновлення інтерфейсу
import logging  # Для логування помилок

# !!! ВАЖЛИВО: Знайди URL твого API на Hugging Face Space !!!
# Коли твій Gradio додаток працює, перейди у вкладку "API" (може бути під кнопкою "...")
# Знайди там API endpoint.
# Він буде виглядати приблизно так:
# https://<твій-логін-hf>-<назва-твого-space>.hf.space/api/predict/
# АБО може бути інший формат, дивись документацію Gradio API для твого Space.
HF_SPACE_API_URL = "СЮДИ_ТРЕБА_ВСТАВИТИ_URL_З_HUGGING_FACE_SPACE"  # ЗАМІНИ ЦЕ!

# Налаштування логування
logging.basicConfig(level=logging.ERROR,  # Логувати тільки помилки (можна змінити рівень)
                    format='%(asctime)s - %(levelname)s - %(message)s')

def send_message():
    user_input = input_field.get("1.0", tk.END).strip()  # Отримати текст з поля вводу
    if not user_input:
        return  # Не відправляти порожні повідомлення

    chat_area.config(state=tk.NORMAL)  # Дозволити редагування поля чату
    chat_area.insert(tk.END, f"Ти: {user_input}\n")  # Додати повідомлення користувача
    input_field.delete("1.0", tk.END)  # Очистити поле вводу
    chat_area.config(state=tk.DISABLED)  # Заборонити редагування
    chat_area.see(tk.END)  # Прокрутити вниз

    # Показуємо, що йде запит
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "Бот: думає...\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

    # Функція для відправки запиту (виконується у окремому потоці)
    def fetch_response():
        try:
            if not HF_SPACE_API_URL or "СЮДИ_ТРЕБА_ВСТАВИТИ_URL" in HF_SPACE_API_URL:
                raise ValueError("URL для API Hugging Face не вказано або не замінено у коді!")

            # Дані для Gradio API (формат може відрізнятися, дивись документацію твого Space API)
            payload = {"data": [user_input]}

            response = requests.post(HF_SPACE_API_URL, json=payload, timeout=60)  # timeout 60 секунд
            response.raise_for_status()  # Перевірити на HTTP помилки (4xx, 5xx)

            result = response.json()

            # Отримати відповідь бота (формат залежить від Gradio API)
            # Дивись приклад відповіді у документації твого Space API
            if 'data' in result and isinstance(result['data'], list) and result['data']:
                bot_response = result['data'][0]
            else:
                bot_response = "(не вдалося розібрати відповідь від API)"
                logging.error(f"Повна відповідь від API: {result}")  # Логування помилки

        except requests.exceptions.RequestException as e:
            bot_response = f"(Помилка мережі: {e})"
            logging.error(f"Помилка мережі: {e}")  # Логування помилки
        except ValueError as e:
            bot_response = f"(Помилка конфігурації: {e})"
            logging.error(f"Помилка конфігурації: {e}")  # Логування помилки
        except Exception as e:
            bot_response = f"(Невідома помилка: {e})"
            logging.exception(f"Невідома помилка: {e}")  # Логування помилки

        # --- Відображення відповіді (в головному потоці GUI) ---
        window.after(0, display_response, bot_response)

    # Запускаємо відправку запиту в окремому потоці
    threading.Thread(target=fetch_response).start()

def display_response(bot_response):
    chat_area.config(state=tk.NORMAL)
    # Видаляємо "думає..." (знайти останній рядок і замінити)
    # Це простий спосіб, може бути не ідеальним
    chat_content = chat_area.get("1.0", tk.END)
    last_newline_index = chat_content.rfind("Бот: думає...")
    if last_newline_index != -1:
        chat_area.delete(f"{last_newline_index}.0", tk.END)
    chat_area.insert(tk.END, f"Бот: {bot_response}\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

window = tk.Tk()
window.title("Чат з ботом")

# Розмір вікна (можна змінювати)
window.geometry("600x400")

# Створення віджета для відображення чату
chat_area = scrolledtext.ScrolledText(window, state=tk.DISABLED, height=20)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Створення поля для введення повідомлень
input_field = tk.Text(window, height=3)
input_field.pack(padx=10, pady=5, fill=tk.X)

# Створення кнопки для відправки повідомлення
send_button = tk.Button(window, text="Відправити", command=send_message)
send_button.pack(padx=10, pady=5)

# Обробка натискання Enter для відправки повідомлення
def on_enter(event):
    send_message()

input_field.bind("<Return>", on_enter)

window.mainloop()