# desktop_client.py
import tkinter as tk
from tkinter import scrolledtext
import requests # Бібліотека для відправки запитів в інтернет

# !!! ВАЖЛИВО: Знайди URL твого API на Hugging Face Space !!!
# Коли твій Gradio додаток працює, перейди у вкладку "API" (може бути під кнопкою "...")
# Знайди там API endpoint. Він буде виглядати приблизно так:
# https://<твій-логін-hf>-<назва-твого-space>.hf.space/api/predict/ 
# АБО може бути інший формат, дивись документацію Gradio API для твого Space.
HF_SPACE_API_URL = "СЮДИ_ТРЕБА_ВСТАВИТИ_URL_З_HUGGING_FACE_SPACE" # ЗАМІНИ ЦЕ!

def send_message():
    user_input = input_field.get("1.0", tk.END).strip() # Отримати текст з поля вводу
    if not user_input:
        return # Не відправляти порожні повідомлення

    chat_area.config(state=tk.NORMAL) # Дозволити редагування поля чату
    chat_area.insert(tk.END, f"Ти: {user_input}\n") # Додати повідомлення користувача
    input_field.delete("1.0", tk.END) # Очистити поле вводу
    chat_area.config(state=tk.DISABLED) # Заборонити редагування
    chat_area.see(tk.END) # Прокрутити вниз

    # Показуємо, що йде запит
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"Бот: думає...\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)
    window.update_idletasks() # Оновити інтерфейс негайно

    # --- Відправка запиту на Hugging Face ---
    try:
        if not HF_SPACE_API_URL or "СЮДИ_ТРЕБА_ВСТАВИТИ_URL" in HF_SPACE_API_URL:
             raise ValueError("URL для API Hugging Face не вказано або не замінено у коді!")

        # Дані для Gradio API (формат може відрізнятися, дивись документацію твого Space API)
        payload = {"data": [user_input]} 

        response = requests.post(HF_SPACE_API_URL, json=payload, timeout=60) # timeout 60 секунд
        response.raise_for_status() # Перевірити на HTTP помилки (4xx, 5xx)

        result = response.json()

        # Отримати відповідь бота (формат залежить від Gradio API)
        # Дивись приклад відповіді у документації твого Space API
        if 'data' in result and isinstance(result['data'], list) and result['data']:
             bot_response = result['data'][0]
        else:
             bot_response = "(не вдалося розібрати відповідь від API)"
             print("Повна відповідь від API:", result) # Вивести в консоль для діагностики

    except requests.exceptions.RequestException as e:
        bot_response = f"(Помилка мережі: {e})"
    except ValueError as e:
         bot_response = f"(Помилка конфігурації: {e})"
    except Exception as e:
        bot_response = f"(Невідома помилка: {e})"
        print("Повна відповідь від API перед помилкою (якщо є):", result if 'result' in locals() else 'немає')


    # --- Відображення відповіді ---
    chat_area.config(state=tk.NORMAL)
    # Видаляємо "думає..." (знайти останній рядок і замінити)
    # Це простий спосіб, може бути не ідеальним
    chat_content = chat_area.get("1.0", tk.END)
    last_line_start = chat_content.rfind("Бот: думає...")
    if last_line_start != -1:
         chat_area.delete(f"{last_line_start}.0", tk.END)

    chat_area.insert(tk.END, f"Бот: {bot_response}\n") # Додати відповідь бота
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END) # Прокрутити вниз

# --- Створення головного вікна ---
window = tk.Tk()
window.title("Мій Чат Клієнт v0.0.1")
window.geometry("500x600") # Розмір вікна

# --- Створення області чату ---
chat_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, state=tk.DISABLED) # wrap=tk.WORD - перенос слів
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# --- Створення рамки для поля вводу і кнопки ---
input_frame = tk.Frame(window)
input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

# --- Створення поля для вводу ---
input_field = tk.Text(input_frame, height=3) # Висота - 3 рядки
input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

# --- Створення кнопки "Відправити" ---
send_button = tk.Button(input_frame, text="Відправити", command=send_message)
send_button.pack(side=tk.RIGHT)

# Прив'язка Enter до відправки повідомлення (Shift+Enter для нового рядка)
def on_enter_key(event):
     send_message()
     return "break" # Запобігти стандартній обробці Enter (новий рядок)

input_field.bind("<Return>", on_enter_key) # Звичайний Enter
input_field.bind("<KP_Enter>", on_enter_key) # Enter на цифровій клавіатурі

# --- Запуск головного циклу програми ---
window.mainloop()