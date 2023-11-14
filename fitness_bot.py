from aiogram.types import Message, ReplyKeyboardRemove
import logging.handlers
import logging
import os
import aiogram
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
import dotenv
import keyboards
from yoomoney import Client
import asyncio
from datetime import datetime, timedelta
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler


class BlackListMiddleware(BaseMiddleware):
    """
    Middleware, запрещающий пользователям использовать бота после покупки. """

    def __init__(self):
        super(BlackListMiddleware, self).__init__()

    async def on_process_message(self, msg: Message, data: dict):
        """
        Этот Handler вызывается во время получения нового сообщения.
        """

        if msg.from_user.id in black_list:
            await msg.answer("Ты недавно уже покупал фитнес программу! ❌ \nПопробуй позже.")
            raise CancelHandler()


dotenv.load_dotenv()  # Загружаем файл .env


token = os.environ["YOOMONEY_TOKEN"]
client = Client(token)


# Логирование.
logger = logging.getLogger(__name__)

# Записываем в переменную результат логирования
os.makedirs("Logs", exist_ok=True)

# Cоздаёт все промежуточные каталоги, если они не существуют.
logging.basicConfig(  # Чтобы бот работал успешно, создаём конфиг с базовыми данными для бота
    level=logging.INFO,
    format="[%(levelname)-8s %(asctime)s at           %(funcName)s]: %(message)s",
    datefmt="%d.%d.%Y %H:%M:%S",
    handlers=[logging.handlers.RotatingFileHandler("Logs/     TGBot.log", maxBytes=10485760, backupCount=0),
    logging.StreamHandler()])
    

# Создаём Telegram бота и диспетчер:
Bot = aiogram.Bot(os.environ["TOKEN"])
DP = aiogram.Dispatcher(Bot, storage=MemoryStorage())
DP.setup_middleware(BlackListMiddleware())
USERS_BGTASKS = {}
prices = {"Грудь": 2, "Ноги": 2, "Пресс": 2, "Руки": 2, "Спина + плечи": 2, "Фулбади": 2}
black_list = []


class UserState(StatesGroup):  # Создаём состояния
    intensivity = State()


async def check_operation(user_id, state, message_id):

    data = await state.get_data()

    while True:  # Создаем цикл
        history = client.operation_history(label=str(user_id))
        if history.operations:
            print("Operation:",history.operations[0].operation_id)
            print("\tStatus     -->", history.operations[0].status)
            print("\tDatetime   -->", history.operations[0].datetime + timedelta(seconds=30) + timedelta(hours=3), datetime.now())
            if history.operations[0].status == "success" and history.operations[0].datetime + timedelta(seconds=180) + timedelta(hours=3) > datetime.now():
                await Bot.send_message(user_id, f'Ты купил программу "{data["program"]}" с интенсивностью {data["intensivity"]} \
                \nТы сможешь купить следующую фитнес тренировку только через пару минут ❗️', reply_markup=ReplyKeyboardRemove())
                #await Bot.send_message(4356565, f'Куплена программа тренировок "{data["program"]}" с интенсивностью "{data["intensivity"]}" у бота @SILAMUJIKOV.')
                await Bot.delete_message(user_id, message_id)
                black_list.append(user_id)
                await asyncio.sleep(90)
                black_list.remove(user_id)
                await state.finish()
                USERS_BGTASKS[user_id].cancel()
                del USERS_BGTASKS[user_id]

        await asyncio.sleep(10)


@DP.message_handler(commands=["start"])      # КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
async def start(msg: Message):

    await msg.answer("Привет 👋. Я Telegram Bot с программами тренировок на дому. Чтобы начать, выбери интенсивность тренировок: ", reply_markup=keyboards.choose_intensity)
    await UserState.intensivity.set()


@DP.message_handler(state=UserState.intensivity)
async def ReplyKeyboard_handling(msg: Message, state: FSMContext):

    if msg.text in ['Лёгкая 🟢', 'Средняя 🟠', 'Сложная 🔴']:
        await state.update_data(intensivity=msg.text[:-2])
        await msg.answer("Выбери программу: ", reply_markup=keyboards.choose_program)
        await state.reset_state(False)
    else:
        await state.finish()


@DP.message_handler()
async def program_handling(msg: Message, state: FSMContext):

    if msg.from_user.id in USERS_BGTASKS:
        USERS_BGTASKS[msg.from_user.id].cancel()
        del USERS_BGTASKS[msg.from_user.id]

    await state.update_data(program=msg.text[:-2])
    data = await state.get_data()
    message = await Bot.send_photo(chat_id=msg.from_user.id, photo=open("{}.jpg".format(msg.text[:-2]), "rb"), 
    caption=f'Данная программа включает в себя тренировку "{msg.text[:-2]}" с интенсивностью "{data["intensivity"]}".', reply_markup=keyboards.generate_yoomoney_menu(msg.from_user.id, prices[msg.text[:-2]]))
    USERS_BGTASKS[msg.from_user.id] = asyncio.create_task(check_operation(msg.from_user.id, state, message.message_id)) # Запускаем фоновую задачу  
        

if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение