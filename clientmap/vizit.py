from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, list_with_amount_for_poly, touch_send_application, design_application, \
    application
from count_price import count_price_of_vizit
from datetime import datetime, timedelta
import os
import os.path


class FSMClientVizit(StatesGroup):
    amount = State()
    choice = State()
    files = State()
    application = State()
    design_application = State()


async def get_amount_vizit(message: types.Message, state=FSMContext):
    amount_bottom = ['500шт', '1000шт ⭐', '2000шт', '3000шт', '4000шт', '5000шт', '10000шт']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(*amount_bottom)
    await FSMClientVizit.amount.set()
    sticker = data_from_bot.get_content_for_client('sticker_vizit')
    await bot.send_sticker(message.chat.id, sticker=sticker[0])
    await bot.send_message(message.chat.id,
                           'Цены:\n500шт - 1200 руб.\n1000шт - 1400 руб.\n2000шт - 2100 руб.\n3000шт - 3400 руб.\n4000шт '
                           '- 4100 руб.\n5000шт - 5400 руб.\n10000шт - 8100 руб.\n\nВыберите тираж:',
                           reply_markup=mark_up)


async def ask_about_layout(message: types.Message, state=FSMContext):
    if message.text.split()[0] in list_with_amount_for_poly:
        async with state.proxy() as data:
            data['Услуга'] = 'Визитки'
            data['Тираж'] = message.text.split()[0]
            data['Стоимость'] = count_price_of_vizit(message.text)
        choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        mark_up.add(*choice_bottom)
        sticker = data_from_bot.get_content_for_client('sticker_design')
        await FSMClientVizit.choice.set()
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, 'У вас есть дизайн макет?', reply_markup=mark_up)
    else:
        await message.reply('Выберите тираж!')


async def get_design_layout(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if message.text == 'Заказать макет у дизайнера 👩🏻‍🎨':
            data['Дизайнер'] = ''
            await FSMClientVizit.design_application.set()
            await bot.send_message(message.chat.id, 'Стоимость одностороннего макета 700р, для двухсторонего 1200р.\n'
                                                    'Опишите что бы вы хотели.',
                                   reply_markup=touch_send_application)
        elif message.text == 'Всё в наличии. Перейди к оформлению ✅':
            try:
                os.mkdir('files/{}{}'.format(str(message.from_user.username), message.from_user.id))
                os.mkdir(
                    'files/{}{}/{}'.format(str(message.from_user.username), message.from_user.id, data['Услуга']))
                os.mkdir(
                    'files/{}{}/{}/{}'.format(str(message.from_user.username), message.from_user.id, data['Услуга'],
                                              data['Тираж']))
            except FileExistsError:
                pass
            await FSMClientVizit.files.set()
            await bot.send_message(message.chat.id, 'Пришлите файл. Рекомендавано Расширения TIFF, CMD...',
                                   reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).
                                   add(types.KeyboardButton('Завершить загрузку 📶')))


async def get_layout_files(message: types.Message, state=FSMContext):
    try:
        if message.text != '/start':
            async with state.proxy() as data:
                file_path = 'files/{}{}/{}/{}'.format(str(message.from_user.username), message.from_user.id,
                                                      data['Услуга'], data['Тираж'])
                if message.document:
                    img_id = await bot.get_file(message.document.file_id)
                    foo, extension = img_id.file_path.split('.')
                    saved_image = '{}/{}{}'.format(file_path, img_id.file_id, f'.{extension}')
                    await message.document.download(f'{saved_image}')
                    await bot.send_message(message.chat.id, 'Макет получен. Ура!')
                elif message.text:
                    if message.text == 'Завершить загрузку 📶':
                        file_path_os = os.listdir(path=file_path)
                        if len(file_path_os) > 0:
                            ready_date = datetime.today() + timedelta(days=+6)
                            await FSMClientVizit.application.set()
                            await bot.send_message(message.chat.id,
                                                   f'Заявка сформиравана. Производство занимает 3-5 рабочих дней. '
                                                   f'Максимальная дата выдачи: {ready_date.strftime("%d.%m")}\n'
                                                   f'Отправить?', reply_markup=touch_send_application)
                        else:
                            await message.reply('Отправьте макет!')
        else:
            await state.finish()
            await client.create_main_bottom(message)
    except:
        await FSMClientVizit.files.set()
        await message.reply('Отправьте мне макет.')


def vizit_register_handlers(dp: Dispatcher):
    dp.register_message_handler(main_decorator(get_amount_vizit), state=None)
    dp.register_message_handler(main_decorator(ask_about_layout), state=FSMClientVizit.amount)
    dp.register_message_handler(main_decorator(get_design_layout), state=FSMClientVizit.choice)
    dp.register_message_handler(get_layout_files, content_types=['document', 'text'], state=FSMClientVizit.files)
    dp.register_message_handler(main_decorator(design_application), state=FSMClientVizit.design_application)
    dp.register_message_handler(main_decorator(application), state=FSMClientVizit.application)
