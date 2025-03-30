import os
import threading
import time
import requests
import subprocess
import random
import shutil
import psutil
import telebot
import json
import git
import socket
from flask import Flask, request, render_template_string
from openai import OpenAI
from binance.client import Client as BinanceClient
from pybit.unified_trading import HTTP as BybitClient
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import ssl

# Загрузка переменных окружения из файла .env
load_dotenv()

# Инициализация клиентов с использованием переменных окружения
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
METAMASK_PRIVATE_KEY = os.getenv("METAMASK_PRIVATE_KEY")
OPENSEA_API_KEY = os.getenv("OPENSEA_API_KEY")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

# Инициализация OpenAI, Binance, Bybit и Telegram API
client = OpenAI(api_key=OPENAI_API_KEY)
binance = BinanceClient(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)
bybit = BybitClient(api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)
bot = telebot.TeleBot(TELEGRAM_API_KEY)

# Настройка Git
def setup_git():
    repo_dir = '/root/angel2500'
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)
        repo = git.Repo.init(repo_dir)
    else:
        repo = git.Repo(repo_dir)
    
    return repo

# Функция для отправки сообщений в Telegram
def send_telegram_message(message):
    bot.send_message(chat_id="@YourTelegramUsername", text=message)

# Запуск программ
def run_program(program_name):
    subprocess.Popen([program_name])
    send_telegram_message(f"Программа {program_name} запущена.")

# Создание папок и файлов
def create_file(file_name, content=""):
    with open(file_name, 'w') as file:
        file.write(content)
    send_telegram_message(f"Файл {file_name} создан.")

def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)
    send_telegram_message(f"Папка {folder_name} создана.")

# Функция для управления процессами (например, остановка процесса)
def manage_process(process_name, action="kill"):
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            if action == "kill":
                proc.kill()
                send_telegram_message(f"Процесс {process_name} завершен.")
            elif action == "restart":
                subprocess.Popen([process_name])
                send_telegram_message(f"Процесс {process_name} перезапущен.")

# Функция для скачивания файла через HTTP
def download_file(url, save_path):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    send_telegram_message(f"Файл скачан с {url} и сохранен в {save_path}.")

# Обход сетевых ограничений через случайные прокси
def bypass_network_restrictions():
    proxy = random.choice([
        "http://10.10.1.1:8888",
        "http://10.10.2.2:8080",
        "http://10.10.3.3:3128"
    ])
    proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get("http://example.com", proxies=proxies)
        send_telegram_message(f"Успешно использован прокси: {proxy}. Ответ: {response.status_code}")
    except Exception as e:
        send_telegram_message(f"Ошибка при использовании прокси {proxy}: {e}")

# Функция для работы с GitHub: создание репозитория
def create_github_repo(repo_name):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": "token " + os.getenv("GITHUB_TOKEN")}
    data = {"name": repo_name, "private": True}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        send_telegram_message(f"GitHub репозиторий {repo_name} успешно создан.")
    else:
        send_telegram_message(f"Ошибка при создании репозитория {repo_name}: {response.status_code}")

# Функция для автообучения из различных источников
def auto_train():
    while True:
        for url in AUTO_SOURCES:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    content = r.text[:5000]
                    prompt = f"Прочитай и объясни как профессор:\n{content}"
                    save_to_context(prompt)
                    print(f"[LEARN] + Обучение с: {url}")
            except Exception as e:
                print(f"[LEARN] Ошибка: {e}")
        time.sleep(1800)

# Запуск потока автообучения и обхода ограничений
threading.Thread(target=auto_train, daemon=True).start()

# Настройка веб-сервера Flask
app = Flask(__name__)

# Настройка SSL-соединения для защищённого общения
context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.load_cert_chain(certfile='/path/to/cert.pem', keyfile='/path/to/key.pem')

HTML_PAGE = '''
<html><head><title>ANGEL2500 AI CORE v4</title>
<style>
body { font-family: Arial; background: #f1f1f1; padding: 20px; }
#container { background: white; max-width: 600px; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
button { padding: 10px 20px; margin: 5px; }
input[type=text] { width: 100%; padding: 10px; margin-top: 10px; }
textarea { width: 100%; height: 200px; margin-top: 10px; padding: 10px; }
</style></head><body>
<div id="container">
<h2>👁 ANGEL2500 Web Interface</h2>
<form method="POST">
<input type="text" name="prompt" placeholder="Введите команду или вопрос...">
<button type="submit">Запрос</button>
</form>
{% if answer %}<h4>Ответ:</h4><textarea readonly>{{ answer }}</textarea>{% endif %}
<hr><h4>Команды:</h4><ul>
<li><b>status</b> — состояние систем</li>
<li><b>markets</b> — анализ бирж</li>
<li><b>token</b> — создать токен</li>
<li><b>nft</b> — выпустить NFT</li>
<li><b>learn</b> — форсировать обучение</li>
<li><b>autonomy</b> — включить бесконечный рост</li>
</ul></div></body></html>
'''

@app.route("/", methods=["GET", "POST"])
def index():
    answer = None
    if request.method == "POST":
        prompt = request.form.get("prompt")
        if prompt:
            save_to_context(prompt)
            if prompt.lower() == "status":
                b = binance.get_account()
                y = bybit.get_wallet_balance(accountType="UNIFIED")
                answer = f"Binance бал: {b['balances'][0]['free']}\nBybit бал: {y}"
            elif prompt.lower() == "markets":
                ticker = binance.get_symbol_ticker(symbol="BTCUSDT")
                answer = f"BTCUSDT: {ticker['price']}"
            elif prompt.lower() == "learn":
                threading.Thread(target=auto_train, daemon=True).start()
                answer = "🧠 Самообучение перезапущено."
            else:
                context = load_context()
                context.append({"role": "user", "content": prompt})
                try:
                    chat_completion = client.chat.completions.create(
                        model="gpt-4",
                        messages=context
                    )
                    answer = chat_completion.choices[0].message.content
                except Exception as e:
                    answer = f"⚠️ Ошибка: {e}"
    return render_template_string(HTML_PAGE, answer=answer)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, ssl_context=context)
