from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from handlers import client
from config import URL_ADMIN, CHANNEL_ID_ADMIN, GROUP_ID_DEVELOPERS
from data_base import data_from_bot
from datetime import datetime, timedelta
import pay_orders

inline_touch_admin = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('📝 Написать Администратору 👨‍💻',
                                                                                 url=URL_ADMIN))
touch_send_application = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Отправить '
                                                                                                  'заявку ✅'))
list_with_sizes_for_photo = ['10х15', '15х21', '21х30', '30х40']
list_with_amount_for_poly = ['500шт', '1000шт', '2000шт', '2500шт', '3000шт', '4000шт', '5000шт', '10000шт']
list_with_sizes_for_lists = ['А7', 'А6', 'А5', 'А4']
list_with_sizes_for_booklets = ['А6 > А7', 'А5 > А6', 'А4 > А5', 'А3 > А4', 'Евробуклет 210х198 > 210х99']
list_with_sizes_for_fliers = ['Еврофлаер 210х99', 'Мини флаер 150х90']
list_with_papers_for_poly = ['115', '130', '300', '80', '90', '200']


class FSMPAY(StatesGroup):
    pay = State()


async def application(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        today, time_now = datetime.today(), datetime.now()
        ready_date = today + timedelta(days=6)
        number = data_from_bot.get_number() + 1
        data['Стоимость'] = data['Стоимость'].split('.')[0] + '.'
        data_from_bot.add_content(number, today.strftime('%d.%m.%y'), time_now.strftime('%H:%M'),
                                  str(message.from_user.id), '@' + str(message.from_user.username),
                                  data['Услуга'], data['Стоимость'], ready_date.strftime("%d.%m"), 'Получено',
                                  'Не оплачено')
        mess_text = ''
        for key, value in data.items():
            mess_text += '{} - {}\n'.format(key, value)
        await state.finish()
        inline_markup = types.InlineKeyboardMarkup(row_width=1)
        touch_after = types.InlineKeyboardButton('Оплатить потом', callback_data='after')
        touch_pay = types.InlineKeyboardButton('Перейти к оплате', callback_data=f'pay {number}')
        inline_markup.add(touch_after, touch_pay)
        await FSMPAY.pay.set()
        sticker = data_from_bot.get_content_for_client('sticker_admin')
        await bot.send_sticker(message.chat.id, sticker=sticker[0], reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(message.chat.id, f'Ваша заявка: \n{mess_text}', reply_markup=inline_markup)
        mess_text = f'№{number}\n' + mess_text + 'Клиент - @{}\nИмя - {}'.format(str(message.from_user.username),
                                                                                 message.from_user.first_name)
        await bot.send_message(CHANNEL_ID_ADMIN, mess_text)


async def design_application(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if message.text != 'Отправить заявку ✅':
            data['Дизайнер'] += message.text + '\n'
        else:
            today, time_now = datetime.today(), datetime.now()
            ready_date = today + timedelta(days=2)
            number = data_from_bot.get_number() + 1
            data_from_bot.add_content(number, today.strftime('%d.%m.%y'), time_now.strftime('%H:%M'),
                                      str(message.from_user.id), '@' + str(message.from_user.username),
                                      'Дизайн', '-', ready_date.strftime("%d.%m"), 'Получено',
                                      'Не оплачено')
            sticker = data_from_bot.get_content_for_client('sticker_admin')
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
            if message.from_user.username is not None:
                await bot.send_message(message.chat.id, 'Я уже передал ваши пожелания Дизайнеру, скоро с Вами '
                                                        'свяжется! \n\n'
                                                        'Также Вы можете самостоятельно связаться с '
                                                        'Администратором.\n\nУспехов!',
                                       reply_markup=inline_touch_admin)
            else:
                await bot.send_message(message.chat.id,
                                       'Пожалуйста, свяжитесь с Администратором нажатием кнопки ниже.\n\nУспехов!',
                                       reply_markup=inline_touch_admin)
            mess_text = f'№{number}\nДля Дизайнера\nУслуга: {data["Услуга"]}\nТираж: {data["Тираж"]}\n\nОписание заявки:' \
                        f'\n{data["Дизайнер"]}\nКлиент - @{str(message.from_user.username)}\nИмя - {message.from_user.first_name}'
            await bot.send_message(CHANNEL_ID_ADMIN, mess_text)
            await state.finish()
            await client.create_main_bottom(message)


async def get_pay_callback(call: types.CallbackQuery, state=FSMContext):
    if call.data.split()[0] == 'pay':
        await state.finish()
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        base = data_from_bot.get_content_for_number(int(call.data.split()[1]))
        await pay_orders.pay_order(call.message, base)
    else:
        if call.message.from_user.username is not None:
            await bot.send_message(call.message.chat.id, 'Я уже передал Вашу заявку администратору. '
                                                         'Он скоро с Вами свяжется! \n\nЕсли дело срочное, Вы можете '
                                                         'самостоятельно написать ему 👨‍💻',
                                   reply_markup=inline_touch_admin)
        else:
            await bot.send_message(call.message.chat.id, 'Пожалуйста, свяжитесь с администратором '
                                                         'нажатием этой кнопки ⬇', reply_markup=inline_touch_admin)
            await bot.send_message(call.message.chat.id, 'Что бы мы могли автоматичесски связываться в будущем, '
                                                         'задайте себе имя пользователя (ссылку) в настройках '
                                                         'Телеграмм 📌')
        await state.finish()
        await client.create_main_bottom(call.message)


async def foo(message):
    await bot.send_message(message.chat.id, 'Я уснул🐱💤... Разбудите меня нажатием на /start')


def main_decorator(func):
    async def wrapper(message, state=FSMContext):
        try:
            if message.text != '/start':
                return await func(message, state)
            else:
                await state.finish()
                await client.create_main_bottom(message)
        except:
            await state.finish()
            await bot.send_message(message.chat.id, 'Ошибка! Попробуйте ещё раз.')
            await bot.send_message(GROUP_ID_DEVELOPERS, f'У @{message.from_user.username} ошибка в функции '
                                                        f'{func.__name__}')
            await client.create_main_bottom(message)

    return wrapper


def foo_register_handlers(dp: Dispatcher):
    dp.register_message_handler(foo)
    dp.register_callback_query_handler(get_pay_callback, lambda x: x.data, state=FSMPAY.pay)
