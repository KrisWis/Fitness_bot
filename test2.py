from aiogram.types import Message, CallbackQuery
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
prices = {"Грудь": 2, "Ноги": 2, "Пресс": 2, "Руки": 2, "Спина + плечи": 2, "Фулбади": 2}


class UserState(StatesGroup):  # Создаём состояния
    intensivity = State()


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
    await state.update_data(program=msg.text[:-2])
    data = await state.get_data()
    await Bot.send_photo(chat_id=msg.from_user.id, photo=open("{}.jpg".format(msg.text[:-2]), "rb"), 
    caption=f'Данная программа включает в себя тренировку "{msg.text[:-2]}" с интенсивностью "{data["intensivity"]}".', reply_markup=keyboards.generate_yoomoney_menu(msg.from_user.id, prices[msg.text[:-2]]))


@DP.callback_query_handler()
async def callback_worker(call: CallbackQuery, state: FSMContext):
    if call.data == "Проверить оплату":
        data = await state.get_data()
        last_operation = client.operation_history(label=str(call.from_user.id)).operations

        try:
            if last_operation.status == "success":

                await call.message.edit_text(f'Ты купил программу "{data["program"]}" с интенсивностью {data["intensivity"]}')
                await Bot.send_message(4356565, f'Куплена программа тренировок "{data["program"]}" с интенсивностью "{data["intensivity"]}" у бота @SILAMUJIKOV.')
                await state.finish()
            else:
                await call.message.answer("Ты не оплатил покупку! ❌")
        except:
            await call.message.answer("Ты не оплатил покупку! ❌")


if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение