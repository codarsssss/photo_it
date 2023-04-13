from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from count_price import count_price_of_light_box
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, touch_send_application, application, design_application
from datetime import datetime, timedelta
import os
import os.path


class FSMClientLight(StatesGroup):
    size = State()
    choice = State()
    files = State()
    application = State()
    design_application = State()


async def get_size_light_box(message: types.Message, state=FSMContext):
    sticker = data_from_bot.get_content_for_client('sticker_light_box')
    await FSMClientLight.size.set()
    await bot.send_sticker(message.chat.id, sticker=sticker[0])
    await bot.send_message(message.chat.id, 'Напишите нужный размер в сантиметрах через пробел.\nПример: 80 120',
                           reply_markup=types.ReplyKeyboardRemove())


async def get_choice_design(message: types.Message, state=FSMContext):
    try:
        x, y = message.text.split()
        if x.isdigit() and y.isdigit():
            async with state.proxy() as data:
                data['Услуга'] = 'Световой короб'
                data['Размер'] = f'{x}x{y}'
                data['Стоимость'] = count_price_of_light_box(int(x), int(y))
            choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            mark_up.add(*choice_bottom)
            await FSMClientLight.choice.set()
            await bot.send_message(message.chat.id, f'Согласно выбранным параметрам, стоимость составит:\n'
                                                    f'*{data["Стоимость"]}*\n\nУ вас есть дизайн макет?',
                                   reply_markup=mark_up, parse_mode='Markdown')
        else:
            await message.reply('Введите размер корректно\nВ сантиметрах через пробел.\nПример: 80 120')
    except:
        await message.reply('Введите размер корректно два числа: ширина и высота\nПример: 80 120')


async def get_design_layout(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if message.text == 'Заказать макет у дизайнера 👩🏻‍🎨':
            data['Дизайнер'] = ''
            await FSMClientLight.design_application.set()
            await bot.send_message(message.chat.id, 'Стоимость одностороннего макета 700р, для двухсторонего 1200р.\n'
                                                    'Опишите что бы вы хотели.',
                                   reply_markup=touch_send_application)
        elif message.text == 'Всё в наличии. Перейди к оформлению ✅':
            try:
                os.mkdir('files/{}{}'.format(str(message.from_user.username), message.from_user.id))
                os.mkdir(
                    'files/{}{}/{}'.format(str(message.from_user.username), message.from_user.id, data['Услуга']))
            except FileExistsError:
                pass
            await FSMClientLight.files.set()
            await bot.send_message(message.chat.id, 'Пришлите файл. Рекомендавано Расширения TIFF, CMD...',
                                   reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).
                                   add(types.KeyboardButton('Завершить загрузку 📶')))


async def get_layout_files(message: types.Message, state=FSMContext):
    try:
        if message.text != '/start':
            async with state.proxy() as data:
                file_path = 'files/{}{}/{}'.format(str(message.from_user.username), message.from_user.id,
                                                   data['Услуга'])
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
                            await FSMClientLight.application.set()
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
        await FSMClientLight.files.set()
        await message.reply('Отправьте мне макет.')


def light_box_register_handlers(dp: Dispatcher):
    dp.register_message_handler(main_decorator(get_size_light_box), state=None)
    dp.register_message_handler(main_decorator(get_choice_design), state=FSMClientLight.size)
    dp.register_message_handler(main_decorator(get_design_layout), state=FSMClientLight.choice)
    dp.register_message_handler(get_layout_files, content_types=['document', 'text'], state=FSMClientLight.files)
    dp.register_message_handler(main_decorator(design_application),
                                state=FSMClientLight.design_application)
    dp.register_message_handler(main_decorator(application), state=FSMClientLight.application)
