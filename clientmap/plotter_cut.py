from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from count_price import count_price_of_plotter
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, touch_send_application, application, design_application
from datetime import datetime, timedelta
import os
import os.path


class FSMClientPlotter(StatesGroup):
    color = State()
    size = State()
    choice = State()
    files = State()
    application = State()
    design_application = State()


async def get_color_plotter(message: types.Message, state=FSMContext):
    img = data_from_bot.get_content_for_client('img_plotter')
    await bot.send_photo(message.chat.id, img[0], reply_markup=types.ReplyKeyboardRemove())
    await create_color_bottom(message)


async def create_color_bottom(message: types.Message, state=FSMContext):
    color_id = ['3700', '3732', '3786', '3710', '3762', '3782', '3714', '3738', '3752', '3720', '3740', '3754',
                '3722', '3742', '3750', '3724', '3744', '3756', '3726', '3748', '3718', '3734', '3746', '3792',
                '3730', '3784', '3796']
    mark_up = types.InlineKeyboardMarkup()
    color_bottom = []
    for i in color_id:
        color_touch = types.InlineKeyboardButton(i, callback_data=f'{i}')
        color_bottom.append(color_touch)
    touch_back = types.InlineKeyboardButton('В главное меню', callback_data='main')
    mark_up.add(*color_bottom)
    mark_up.add(touch_back)
    await FSMClientPlotter.color.set()
    await bot.send_message(message.chat.id, 'Выберите цвет плекнки:', reply_markup=mark_up)


async def get_color_callback(call: types.CallbackQuery, state=FSMContext):
    async with state.proxy() as data:
        data['Услуга'] = 'Плоттерная резка'
        if call.data == 'back':
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            await bot.delete_message(call.message.chat.id, data['Удаление'].message_id)
            await create_color_bottom(call.message)
        elif call.data == 'okey':
            del data['Удаление']
            await FSMClientPlotter.size.set()
            await bot.send_message(call.message.chat.id, f'Вы выбрали: {data["Цвет"]}')
            await bot.send_message(call.message.chat.id,
                                   'Напишите нужный размер в сантиметрах через пробел.\nПример: 80 120')
        elif call.data == 'main':
            await state.finish()
            await client.create_main_bottom(call.message)
        else:
            data['Цвет'] = call.data
            await bot.delete_message(call.message.chat.id, call.message.message_id)
            sticker = data_from_bot.get_content_for_client(f'sticker_{call.data}')
            data['Удаление'] = await bot.send_sticker(call.message.chat.id, sticker[0])
            mark_up = types.InlineKeyboardMarkup(row_width=1)
            touch_ok = types.InlineKeyboardButton('Выбрать этот цвет ✅', callback_data='okey')
            touch_back = types.InlineKeyboardButton('Назад', callback_data='back')
            mark_up.add(touch_ok, touch_back)
            await bot.send_message(call.message.chat.id, f'Вот как выглядит цвет: {call.data}', reply_markup=mark_up)


async def get_choice_design(message: types.Message, state=FSMContext):
    try:
        x, y = message.text.split()
        if x.isdigit() and y.isdigit():
            async with state.proxy() as data:
                data['Размер'] = f'{x}x{y}'
                data['Стоимость'] = count_price_of_plotter(int(x), int(y))
            sticker = data_from_bot.get_content_for_client('sticker_plotter')
            choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            mark_up.add(*choice_bottom)
            await FSMClientPlotter.choice.set()
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
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
            await FSMClientPlotter.design_application.set()
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
            await FSMClientPlotter.files.set()
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
                            await FSMClientPlotter.application.set()
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
        await FSMClientPlotter.files.set()
        await message.reply('Отправьте мне макет.')


def plotter_register_handlers(dp: Dispatcher):
    dp.register_message_handler(main_decorator(get_color_plotter), state=None)
    dp.register_callback_query_handler(get_color_callback, lambda x: x.data, state=FSMClientPlotter.color)
    dp.register_message_handler(main_decorator(get_choice_design), state=FSMClientPlotter.size)
    dp.register_message_handler(main_decorator(get_design_layout), state=FSMClientPlotter.choice)
    dp.register_message_handler(get_layout_files, content_types=['document', 'text'], state=FSMClientPlotter.files)
    dp.register_message_handler(main_decorator(design_application), state=FSMClientPlotter.design_application)
    dp.register_message_handler(main_decorator(application), state=FSMClientPlotter.application)
