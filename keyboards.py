from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from yoomoney import Quickpay
choose_intensity = ReplyKeyboardMarkup(resize_keyboard=True)
choose_intensity.add(*['Лёгкая 🟢', 'Средняя 🟠', 'Сложная 🔴'])
choose_program = ReplyKeyboardMarkup(resize_keyboard=True)
choose_program.add(*['Спина + плечи 🦾', 'Ноги 🦵', 'Грудь 🫁', 'Руки 💪', 'Фулбади ✊', 'Пресс 👊'])

def generate_yoomoney_menu(user_id, price):
    yoomoney_menu = InlineKeyboardMarkup(row_width=1)
    quickpay = Quickpay(
                receiver="4100118096065698",
                quickpay_form="shop",
                targets="Покупка фитнес тренировки",
                paymentType="SB",
                sum=price,
                label=str(user_id)
                )
    yoomoney_menu.add(InlineKeyboardButton(
        text="Ссылка на оплату",
        url=quickpay.base_url
    ))
    return yoomoney_menu