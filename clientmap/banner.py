from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from count_price import count_price_of_banner
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, touch_send_application, application, design_application
from datetime import datetime, timedelta
import os
import os.path


class FSMClientBanner(StatesGroup):
    type_material = State()
    size = State()
    grommets = State()
    choice = State()
    files = State()
    application = State()
    design_application = State()


async def get_material_type_banner(message: types.Message, state=FSMContext):
    material_bottom = ['Баннер ламинированный 440 гр/м', 'Баннерная сетка 360 гр/м']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(material_bottom[0])
    mark_up.add(material_bottom[1])
    await FSMClientBanner.type_material.set()
    await bot.send_message(message.chat.id, 'Какой баннер Вам нужен?', reply_markup=mark_up)


async def get_size_banner(message: types.Message, state=FSMContext):
    if message.text in ['Баннер ламинированный 440 гр/м', 'Баннерная сетка 360 гр/м']:
        async with state.proxy() as data:
            data['Услуга'] = 'Баннер'
            data['Материал'] = message.text
        if message.text == 'Баннер ламинированный 440 гр/м':
            sticker = data_from_bot.get_content_for_client('sticker_banner')
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
        else:
            sticker = data_from_bot.get_content_for_client('sticker_banner_grid')
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await FSMClientBanner.size.set()
        await bot.send_message(message.chat.id, 'Напишите нужный размер в сантиметрах через пробел.\nПример: 80 120',
                               reply_markup=types.ReplyKeyboardRemove())


async def get_grommets_banner(message: types.Message, state=FSMContext):
    try:
        x, y = message.text.split()
        if x.isdigit() and y.isdigit():
            async with state.proxy() as data:
                data['Размер'] = f'{x}x{y}'
            touch_grommets = ['Да, повесим', 'Нет, приклеим']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
            mark_up.add(*touch_grommets)
            sticker = data_from_bot.get_content_for_client('sticker_grommets')
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
            await FSMClientBanner.grommets.set()
            await bot.send_message(message.chat.id, 'Вам нужны люверсы?\nПроклейка края входит в стоимость люверсов',
                                   reply_markup=mark_up)
        else:
            await message.reply('Введите размер корректно\nВ сантиметрах через пробел.\nПример: 80 120')
    except:
        await message.reply('Введите размер корректно два числа: ширина и высота\nПример: 80 120')


async def get_choice_design(message: types.Message, state=FSMContext):
    if message.text in ['Да, повесим', 'Нет, приклеим']:
        async with state.proxy() as data:
            x, y = data['Размер'].split('x')
            data['Стоимость'] = count_price_of_banner(int(x), int(y), data['Материал'].split()[0],
                                                      message.text.split(',')[0])
        choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        mark_up.add(*choice_bottom)
        sticker = data_from_bot.get_content_for_client('sticker_design')
        await FSMClientBanner.choice.set()
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, f'Согласно выбранным параметрам, стоимость составит:\n'
                                                f'*{data["Стоимость"]}*\n\nУ вас есть дизайн макет?',
                               reply_markup=mark_up, parse_mode='Markdown')


async def get_design_layout(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if message.text == 'Заказать макет у дизайнера 👩🏻‍🎨':
            data['Дизайнер'] = ''
            await FSMClientBanner.design_application.set()
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
            await FSMClientBanner.files.set()
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
                            await FSMClientBanner.application.set()
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
        await FSMClientBanner.files.set()
        await message.reply('Отправьте мне макет.')


def banner_register_handlers(dp: Dispatcher):
    dp.register_message_handler(main_decorator(get_material_type_banner), state=None)
    dp.register_message_handler(main_decorator(get_size_banner), state=FSMClientBanner.type_material)
    dp.register_message_handler(main_decorator(get_grommets_banner), state=FSMClientBanner.size)
    dp.register_message_handler(main_decorator(get_choice_design), state=FSMClientBanner.grommets)
    dp.register_message_handler(main_decorator(get_design_layout), state=FSMClientBanner.choice)
    dp.register_message_handler(get_layout_files, content_types=['document', 'text'], state=FSMClientBanner.files)
    dp.register_message_handler(main_decorator(design_application),
                                state=FSMClientBanner.design_application)
    dp.register_message_handler(main_decorator(application), state=FSMClientBanner.application)
