"""Главный файл приложения бота."""

import datetime
import logging
import os
import re
import sys
import time
import pytz
import requests
import configparser
import locale


from dotenv import load_dotenv
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from mycustomerror import MyCustomError
from telegram import Bot, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater


load_dotenv()
config = configparser.ConfigParser()
config.read('setup.cfg', encoding='utf-8')


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
LOG_LEVEL = config['log_setting']['log_level']
FORMAT_LOG = config['log_setting']['log_format']
LOGS_DIRECTORY_PATH = config['log_setting']['logs_directory_path']
LOG_SIZE = int(config['log_setting']['log_size'])
BACKUP_СOUNT = int(config['log_setting']['backup_сount'])
TELEGRAM_ADMIN_ID = config['tg_setting']['admin_tg_id']
RETRY_TIME = int(config['default']['retry_time'])
TZ_MOSCOW = pytz.timezone(config['tg_setting']['tzone'])
DT_MOSCOW = datetime.datetime.now(TZ_MOSCOW)
ENDPOINTS = []
CHECK_RESULT = []
BUTTONS = ReplyKeyboardMarkup(
    [['/bot_settings', '/last_check', '/subscribe']],
    resize_keyboard=True,
)
BOT = Bot(token=TELEGRAM_TOKEN)


def get_bot():
    """Проверяет запуск бота и выбрасывает исключение при ошибки запуска."""
    if not BOT:
        message = f'Ошибка инициализации объекта BOT - {BOT}.'
        logger.error(message, exc_info=True)
        raise MyCustomError(message)
    return BOT


def get_subscribers_ids():
    """Достаёт из файла setup.cfg перечень id учётных запписей телеграм."""
    telegram_subscriber_ids = []
    tg_ids = config['tg_setting']['subscription_tg_ids'].split(',')
    for tg_id in tg_ids:
        if isinstance(int(tg_id), int):
            telegram_subscriber_ids.append(int(tg_id))
    logger.debug(
        'Список ИД учёток Телеграм подписчиков из get_subscribers_ids - '
        + f'{telegram_subscriber_ids}.')
    return telegram_subscriber_ids


def send_message_admin(message):
    """Отправляет сообщение в Telegram чат админа."""
    bot = get_bot()
    bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=message,)
    logger.debug(f'Админу отправлено сообщение - "{message}".')


def send_message(message, telegram_ids):
    """Отправляет сообщение в Telegram-чаты участников процесса."""
    bot = get_bot()
    for t in telegram_ids:
        bot.send_message(chat_id=t, text=message,)
    logger.debug(f'Получателям отправлено сообщение - "{message}".')


def check_status_resource(endpoint, telegram_ids):
    """Делает запрос к эндпоинту.

    В качестве параметра функция получает временную метку и ендпоинт. Делает
    запрос и, если статус ответа не 200, то посылает сообщение пользоватлю из
    списка.
    """
    bot = get_bot()
    try:
        response = requests.get(endpoint)
        logger.info(f'response - "{response}". type(response) - {type(response)}.')
        
        result = response.status_code
    except requests.exceptions.ConnectionError as conerror:
        logger.warning(conerror)
        result = f'Connection error: \n{conerror}\n'

    if result != HTTPStatus.OK:
        message_status_code_not_200 = (f'Сайт: "{endpoint}". Ошибка: {result}.')
        logger.warning(message_status_code_not_200)
        send_message(message_status_code_not_200, telegram_ids)
    else:
        logger.info(f'Сайт: "{endpoint}". Ответ: {result}.')
    return result


def check_tokens():
    """Проверяет доступность переменных окружения для работы программы."""
    logger.info('***Работает check_tokens.')
    logger.debug(f'TELEGRAM_TOKEN - {TELEGRAM_TOKEN}.')
    logger.debug(f'TELEGRAM_ADMIN_ID - {TELEGRAM_ADMIN_ID}.')
    return all([TELEGRAM_TOKEN, TELEGRAM_ADMIN_ID])


def last_check(update, context):
    """Возвращает результаты последней проверки."""
    logger.info('***Работает last_check.')
    chat = update.effective_chat
    name = update.message.chat.username
    message = ''.join(CHECK_RESULT)
    context.bot.send_message(
        chat_id=chat.id,
        text=message,
        reply_markup=BUTTONS
    )
    logger.info(
        f'Запрошены результаты последней проверки. Пользователь {name}.')


def bot_settings(update, context):
    """Возвращает список проверяемых сайтов и периодичность проверки."""
    logger.info('***Работает bot_settings.')
    chat = update.effective_chat
    name = update.message.chat.username
    part_name = name[:4]
    endpoints_str = ''
    for e in ENDPOINTS:
        endpoints_str += e + '\n'
    message = (
        f'Список проверямых сайтов:\n{endpoints_str}'
        + f'Периодичность проверки - 1 раз в {RETRY_TIME} ч.')
    context.bot.send_message(
        chat_id=chat.id,
        text=message,
        reply_markup=BUTTONS
    )
    logger.info(
        f'Запрошены настройки бота. Часть имени пользователя {part_name}.')


def subscribe(update, context):
    """Подписка на рассылку сообщений от бота."""
    logger.info('***Работает subscribe.')
    chat = update.effective_chat
    name = update.message.chat.username
    tg_id = update.message.chat.id
    logger.debug(f'tg_id - {tg_id}')
    telegram_ids = get_subscribers_ids()
    logger.debug(f'telegram_ids - {telegram_ids}.')
    tg_setting = config['tg_setting']
    if tg_id in telegram_ids:
        telegram_ids.remove(tg_id)
        logger.debug('telegram_ids после удаления id - '
                     + f'{telegram_ids}.')
        message = ('Вы отписались от рассылки сообщений от бота.')
        logger.info(f'Пользователь {name} отписалися от рассылки.')
    else:
        telegram_ids.append(tg_id)
        logger.debug('telegram_ids id после добавления - '
                     + f'{telegram_ids}.')
        message = ('Вы подписались на рассылку сообщений от бота.')
        logger.info(f'Пользователь {name} подписался на рассылку.')
    tg_setting['subscription_tg_ids'] = ",".join(str(id) for id in telegram_ids)
    with open('setup.cfg', 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    context.bot.send_message(
        chat_id=chat.id,
        text=message,
        reply_markup=BUTTONS
    )


def main():
    """Основная логика работы бота."""
    global ENDPOINTS, CHECK_RESULT
    endpoints = config.get('tg_setting', 'endpoints')
    endpoints = re.split('\\n|,', endpoints)
    for endpoint in endpoints:
        if isinstance(endpoint, str) and len(endpoint) != 0:
            ENDPOINTS.append(endpoint)
    logger.info(f'Список Интернет-сайтов - {[endp for endp in ENDPOINTS]}.')
    telegram_ids = get_subscribers_ids()
    if not check_tokens():
        message = (
            f'Проверка токенов завершилась с ошибкой - {check_tokens()}.')
        logger.critical(message, exc_info=True)
        sys.exit(message)
    logger.info('Проверка токенов завершилась успешно.')
    while True:
        try:
            logger.info('Старт очередной проверки...')
            updater = Updater(token=TELEGRAM_TOKEN)
            date_time = DT_MOSCOW.strftime('%d.%m.%Y %H:%M')
            CHECK_RESULT = [
                'Результаты последней проверки.\n'
                + f'Дата и время: {date_time} (мск).\n'
                + 'Статусы по сайтам:\n'
            ]
            SUCCESSFUL_RESULT = '\n    Успешный доступ:\n'
            UNSUCCESSFUL_RESULT = '\n    ! Проблемы с доступом:\n'
            for endp in ENDPOINTS:
                check = check_status_resource(endp, telegram_ids)
                
                logger.debug(f'endpoint: {endp}, check: {check}, type(check): {type(check)}')
                if check == 200:
                    SUCCESSFUL_RESULT += (f'{check} - {endp}\n')
                else:
                    UNSUCCESSFUL_RESULT += f'{check} - {endp}\n'
            CHECK_RESULT.append(UNSUCCESSFUL_RESULT)
            CHECK_RESULT.append(SUCCESSFUL_RESULT)
            logger.info(f'CHECK_RESULT - {CHECK_RESULT}.')
        except TypeError as typerror:
            message = (f'TypeError при запуске функции main: {typerror}')
            logger.error(message)
            send_message_admin(message)
            logger.exception(typerror, exc_info=True)
        except Exception as error:
            message = (f'Exception при запуске функции main: {error}.')
            logger.error(message)
            send_message_admin(message)
            logger.exception(error, exc_info=True)
        finally:
            updater.dispatcher.add_handler(
                CommandHandler('subscribe', subscribe))
            updater.dispatcher.add_handler(
                CommandHandler('last_check', last_check))
            updater.dispatcher.add_handler(
                CommandHandler('bot_settings', bot_settings))
            updater.start_polling()
            time.sleep(RETRY_TIME * 3600)


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(FORMAT_LOG)
    handler = RotatingFileHandler(
        (LOGS_DIRECTORY_PATH + 'bot.log'),
        maxBytes=LOG_SIZE,
        backupCount=BACKUP_СOUNT,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.info('***\nСтарт работы бота проверки ресурсов ОД.')

    main()
