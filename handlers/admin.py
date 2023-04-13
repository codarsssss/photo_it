from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from data_base import data_from_bot
from config import LIST_ADMIN, GROUP_ID_DEVELOPERS


class FSMAdmin(StatesGroup):
    choice = State()
    date = State()
    number = State()
    status = State()


async def welcome_admin(message: types.Message):
    try:
        if message.from_user.username in LIST_ADMIN:
            await message.answer('Добро пожаловать, Админ.')
            await create_admin_bottom(message)
        else:
            await message.reply('Ты тут не работаешь. Уходи!!!')
    except:
        pass


async def create_admin_bottom(message: types.Message):
    try:
        admin_bottom = ['Выбрать день', 'Изменить статус', 'Заказы в работе']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mark_up.add(*admin_bottom)
        await FSMAdmin.choice.set()
        await message.answer('Чем ещё я могу помочь?', reply_markup=mark_up)
    except:
        pass


async def set_command(message: types.Message, state=FSMContext):
    if message.text == 'Выбрать день':
        await FSMAdmin.date.set()
        await message.answer('Введите дату **.**.**')
    elif message.text == 'Изменить статус':
        await FSMAdmin.number.set()
        await message.answer('Введите номер заказа', reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Заказы в работе':
        answer = data_from_bot.get_in_job()
        if len(answer):
            miss_text = ''
            for info in answer:
                miss_text += f'№{info[0]}\nСтатус: *{info[8]}*, Выдача: {info[7]}\nКлиент: {info[4]}, ' \
                             f'Услуга: {info[5]}, Стоимость: {info[6]}\nВремя: {info[2]}, Оплата: {info[9]}\n\n'
            try:
                await message.answer(miss_text, parse_mode='Markdown')
            except:
                long = len(miss_text) // 4
                await message.answer(miss_text[:long], parse_mode='Markdown')
                await message.answer(miss_text[long:long*2], parse_mode='Markdown')
                await message.answer(miss_text[long*2:long*3], parse_mode='Markdown')
                await message.answer(miss_text[long*3:], parse_mode='Markdown')
        else:
            await message.answer('Все заказы выдали. Молодцы! 😽')
        await state.finish()
        await create_admin_bottom(message)


async def ask_status(message: types.Message, state=FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['number'] = message.text
        status_bottom = ['Принят', 'Согласование макета', 'В печати', 'Ожидает клиента', 'Выдано']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mark_up.add(*status_bottom)
        await FSMAdmin.status.set()
        await message.answer('Выберите новый статус', reply_markup=mark_up)
    else:
        await message.reply('Введите номер заказа. Пример: 69')


async def set_status(message: types.Message, state=FSMContext):
    if message.text in ['Принят', 'Согласование макета', 'В печати', 'Ожидает клиента', 'Выдано']:
        async with state.proxy() as data:
            answer = data_from_bot.setting_status(message.text, data['number'])
            if message.text == 'Ожидает клиента':
                inline_mark_up = types.InlineKeyboardMarkup()
                touch_isee = types.InlineKeyboardButton('Я увидел. Можно не звонить',
                                                        callback_data='Клиент подтвердил оповещение')
                inline_mark_up.add(touch_isee)
                await bot.send_message(answer[0], f'Статус заказа на *{answer[1]}* изменён: *{message.text}*',
                                       reply_markup=inline_mark_up, parse_mode='Markdown')
            else:
                await bot.send_message(answer[0], f'Статус заказа на *{answer[1]}* изменён: *{message.text}*',
                                       parse_mode='Markdown')
        await bot.send_message(message.chat.id, f'Статус изменен на *{message.text}*. Оповещение отпраленно',
                               parse_mode='Markdown')
        await state.finish()
        await create_admin_bottom(message)
    else:
        await message.reply('Выберите кнопкой!')


async def orders_from_db(message: types.Message, state=FSMContext):
    day = message.text
    answer = data_from_bot.get_content_for_admin(day)
    if len(answer):
        miss_text = ''
        for info in answer:
            miss_text += f'№{info[0]}\nСтатус заказа: *{info[8]}*, Дата выдача: {info[7]}\nКлиент: {info[4]}, ' \
                             f'Услуга: {info[5]}, Стоимость: {info[6]}\nВремя: {info[2]}, Оплата: {info[9]}\n\n'
        try:
            await message.answer(miss_text, parse_mode='Markdown')
        except:
            long = len(miss_text) // 4
            await message.answer(miss_text[:long], parse_mode='Markdown')
            await message.answer(miss_text[long:long * 2], parse_mode='Markdown')
            await message.answer(miss_text[long * 2:long * 3], parse_mode='Markdown')
            await message.answer(miss_text[long * 3:], parse_mode='Markdown')
        await state.finish()
        await create_admin_bottom(message)
    else:
        await message.reply('В этот день не было заказов', reply_markup=types.ReplyKeyboardRemove())


def admin_decorator(func):
    async def wrapper(message, state=FSMContext):
        try:
            return await func(message, state)
        except:
            await state.finish()
            await bot.send_message(message.chat.id, 'Ошибка! Попробуйте ещё раз.')
            await bot.send_message(GROUP_ID_DEVELOPERS, f'У Админа ошибка в функции {func.__name__}')
            await create_admin_bottom(message)

    return wrapper


def admin_register_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome_admin, commands=['admin'])
    dp.register_message_handler(admin_decorator(set_command), state=FSMAdmin.choice)
    dp.register_message_handler(admin_decorator(orders_from_db), state=FSMAdmin.date)
    dp.register_message_handler(admin_decorator(ask_status), state=FSMAdmin.number)
    dp.register_message_handler(admin_decorator(set_status), state=FSMAdmin.status)
