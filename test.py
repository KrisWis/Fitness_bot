from aiogram.types import Message, PreCheckoutQuery, ContentType
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


dotenv.load_dotenv()  # Загружаем файл .env

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
SBERBANK_TOKEN = os.environ["SBERBANK_TOKEN"]


class UserState(StatesGroup):  # Создаём состояния
    intensivity = State()


@DP.message_handler(commands=["start"])      # КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
async def start(msg: Message):

    await msg.answer("Привет 👋. Я Telegram Bot с программами тренировок на дому. Чтобы начать, выбери интенсивность тренировок: ", reply_markup=keyboards.choose_intensity)
    await UserState.intensivity.set()


@DP.message_handler(state=UserState.intensivity)
async def ReplyKeyboard_handling(msg: Message, state: FSMContext):

    await state.update_data(intensivity=msg.text[:-2])
    await msg.answer("Выбери программу: ", reply_markup=keyboards.choose_program)
    await state.reset_state(False)


@DP.message_handler()
async def program_handling(msg: Message, state: FSMContext):
    await state.update_data(program=msg.text[:-2])
    data = await state.get_data()
    await Bot.send_photo(chat_id=msg.from_user.id, photo=open("{}.jpg".format(msg.text[:-2]), "rb"), 
    caption=f'Данная программа включает в себя тренировку "{msg.text[:-2]}" с интенсивностью "{data["intensivity"]}".')
    await Bot.send_invoice(msg.from_user.id, title=f'Программа {msg.text[:-2]}.', 
    description=f'Данная программа включает в себя тренировку "{msg.text[:-2]}" с интенсивностью "{data["intensivity"]}".', 
    payload=f"{msg.text[:-2]}_program", provider_token=SBERBANK_TOKEN, currency="RUB", start_parameter="fitness_bot", prices=[{"label": "Руб", "amount": 15000}])


@DP.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await Bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@DP.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(msg: Message,  state: FSMContext):
    data = await state.get_data()
    #await Bot.send_photo(chat_id=msg.from_user.id, photo=open("{}.jpg".format(data["program"]), "rb"), caption=f'Данная программа включает в себя тренировку "{data["program"]}" с интенсивностью "{data["intensivity"]}"')
    await msg.answer(f'Ты купил программу "{data["program"]}" с интенсивностью {data["intensivity"]}')
    await Bot.send_message(4356565, f'Куплена программа тренировок "{data["program"]}" с интенсивностью "{data["intensivity"]}" у бота @SILAMUJIKOV.')


if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение