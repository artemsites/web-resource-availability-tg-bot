# homework_bot
python telegram bot

Бот умеет:
- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

Для запуска требуется подключить модуль со следующими переменными:
- PRACTICUM_TOKEN - токен учётной записи на API Практикум.Домашка,
- TELEGRAM_TOKEN - токен учётной записи бота Телеграм, от которого будет осуществляться рассылка сообщений,
- TELEGRAM_CHAT_ID - ид чата, в который должны отправляться сообщения.
