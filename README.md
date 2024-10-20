# checking_resources_bot

Телеграм-бот обеспечивает проверку доступности интернет-ресурсов путём обращения к их URL.

### Функциональность бота:
- раз в заданный период (в минутах) опрашивается список ресурсов;
- анализируется ответ от ресурсов по кодам HTTP;
- о недоступности ресурсов передаётся сообщение в Telegram по заданным id пользователей;
- об ошибках бота передаётся сообщение в Telegram по заданному id админа;
- имеется 3 кнопки для пользователей:
    - подписаться\отписаться на рассылку информации о статусе интернет-ресурсов;
    - получить информацию о результатах последней проверки;
    - получить информацию об URL проверяемых интрернет-ресурсов и периодичности проверки;
- работа логируется.

## Использование:

0) Скопировать репозиторий:
```bash
git clone https://github.com/Obshee-Delo-IT/resource-availability-tg-bot.git
cd resource-availability-tg-bot
```

1) создать файл `.env` и записать токен учётной записи Телеграм-бота. Формат: `TELEGRAM_TOKEN=<token>`. Пример заполнения файла см. `.env.example`.
Текущий бот https://t.me/BOT_OD_WEBSITES_CHECKER_BOT - токен от него можно спросить info@artemsites.ru или https://t.me/artemsites

2) заполнить файл `setup.cfg` параметрами:
- `[default]`:
    - `retry_time` - период проверки (минуты) доступности ресурсов в часах. Формат: целое число.
- `[tg_setting]`:
    - `admin_tg_id` - Ид учётной записи Телеграм администратора бота. Вввести Ид одной учётной записи. (https://t.me/userinfobot)
    - `subscription_tg_ids` - Ид учётных записей Телеграм пользователей бота, получающих рассылку сообщений о недоступености ресурсов. Ввести как минимум Ид одной учётной записи.
    - `tzone` - часовая зона для отображения метки времени последней проверки доступности ресурсов. Формат: в соответствие с названием зоны пакет pytz.
    - `endpoints` - список URL по которым должна выполняться проверка. Ввести как минимум один URL.
- `[log_setting]`:
    - `log_level` - название уровня журналирования в соответствие с требованиями пакета logging.
    - `log_format` - формат сообщений в файле журнала соответствие с требованиями пакета logging.
    - `logs_directory_path` - директория для хранения файлов журнала.
    - `log_size` - размер лог-файла в байтах.
    - `backup_сount` - резервное количество лог-файлов.

Пример заполнения файла см. `setup.cfg.example`.

### Далее для запуска на сервере:
3) Создать virtual env на hosting, например для <a href="https://timeweb.com/ru/docs/virtualnyj-hosting/prilozheniya-i-frejmvorki/python-ustanovka-virtualenv/">timeweb</a>. По сути две команды:
```bash
wget https://bootstrap.pypa.io/virtualenv/3.4/virtualenv.pyz
python3 virtualenv.pyz venv
```

4) активировать окружение, установить зависимости и запустить через nohup (чтобы не вырубалось от ssh disconnect):
```bash
source venv/bin/activate
pip install -r requirements.txt
nohup python3 bot.py > bot.out 2>&1 &
```

При обновлении бота необходимо завершить запущенный бот (например через htop), а затем:
```bash
git pull
source venv/bin/activate
nohup python3 bot.py > bot.out 2>&1 &
```

### Для локального запуска (windows?)
3) через терминал в папке проекта создать и запустить виртуальное окружение (далее окружение):
- установить окружение командой `pip install pipenv` или `pip install --user pipenv`. Дождаться установки. В ответ должно быть сообщено место установки окружения. Проверить информацию об окружении командой `pipenv --venv`.
- активировать окружение командой `pipenv shell`. Должно отобразиться сообщение "Launching subshell in virtual environment...". При повторном выполнении команды должно отобразиться сообщение "Shell for C:/<путь к папке с вирт. окружением> already activated".
- установить зависимости командой `pipenv sync --dev`. По результатам установки должно отобразиться сообщение "All dependencies are now up-to-date!" и в папке окружения `~\Lib\site-packages` должны установиться требуемые пакеты.

4) из папки проекта запустить модуль через `pipenv run python bot.py`.

5) Для остановки бота в терминале нажать `Ctrl+C` при этом использованная версия библиотеки Телеграм не позволяет корректно завершить процесс и для перезапуска требуется запустить новый терминал и выполнить команды:
- `pipenv shell`,
- `pipenv run python bot.py`

Перечень зависимостей указан в файле Pipfile.

Больше информации о виртуальном окружении pipenv по ссылке https://pipenv.pypa.io/en/latest/.

### Или для локального запуска (macos & linux)
Создать virtual env
```
python3 -m venv venv
```
Активируйте виртуальное окружение
```
source venv/bin/activate
```
Установите зависимости
```
pip install package_name
```
Чтобы установить зависимости из requirements.txt, используйте
```
pip install -r requirements.txt
```
Сохранить список зависимостей вашего проекта, используя команду
```
pip freeze > requirements.txt
```
Деактивация виртуального окружения
```
deactivate
```

Запуск бота
```
python bot.py
```