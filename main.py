from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium_stealth import stealth
import telebot
import requests
from lxml import html
import time
import config

bot = telebot.TeleBot(config.TOKEN)

previous_price = None
xpath = '//*[@id="layoutPage"]/div[1]/div[5]/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div/span/span'

def get_name(url):
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument('--headless')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-logging')
    options.add_argument('--start-maximized')
    options.add_argument('--window-size=1280,800')
    options.add_argument('--user-agent=Chrome')

    driver = webdriver.Chrome(options=options)
    stealth(driver,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.get(url)

    #time.sleep(3)
    price = driver.find_element(By.XPATH, xpath)
    name = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[5]/div[2]/div/div/div[1]/div[2]/h1')
    return price.text[:-1], name.text

def check_price(url):
    global previous_price
    current_price, name = get_name(url)
    if previous_price is None:
        previous_price = current_price
    elif abs(current_price - previous_price) > 99:
        bot.send_message(chat_id, f'📉 Цена товара под названием: \n {name} \n снизилась от {previous_price} до {current_price}.')
        previous_price = current_price

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '🔎 Отправьте URL товара, который хотели бы отслеживать')
    
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global url, chat_id
    chat_id = message.chat.id
    if 'http' in message.text:
        url = message.text
        price, item_name = get_name(url)
        print(price, item_name)
        bot.send_message(chat_id, f'🛒 Товар под названием {item_name} отслеживается...')
        while True:
            check_price(url)
            time.sleep(3600) # Check every hour

bot.polling()