from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, list_with_sizes_for_photo, touch_send_application, application
from count_price import count_price_of_photo
import os
import os.path


class FSMClientPhoto(StatesGroup):
    size = State()
    disclaimer = State()
    photos = State()
    application = State()


async def get_size_photo(message: types.Message, state=FSMContext):
    print(111)
    size_bottom = ['10х15', '15х21', '21х30', '30х40']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(*size_bottom)
    sticker = data_from_bot.get_content_for_client('sticker_size')
    await FSMClientPhoto.size.set()
    await bot.send_sticker(message.chat.id, sticker=sticker[0])
    await bot.send_message(message.chat.id,
                           'Цены:\n10х15 - 30руб.\n15х21 - 60руб.\n21х30 - 120руб.\n30х40 - 490руб.\n\n🐈 сам  '
                           'рассчитаю скидку в зависимости от кол-ва снимков!')
    await bot.send_message(message.chat.id, 'Выберите размер печати кнопками на клавиатуре ↘️',
                           reply_markup=mark_up)


async def get_agreement(message: types.Message, state=FSMContext):
    if message.text in list_with_sizes_for_photo:
        async with state.proxy() as data:
            data['Услуга'] = 'Фотопечать'
            data['Размер'] = message.text
        await FSMClientPhoto.disclaimer.set()
        sticker = data_from_bot.get_content_for_client('sticker_margin')
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, 'Внимание❕ Мы печатаем фото полностью. '
                                                'Если ваша фотография не соответствует соотношениям сторон '
                                                'стандартных форматов, могут остаться белые края, как на примере. '
                                                'Нажмите кнопку ниже для продолжения.',
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).
                               add(types.KeyboardButton('Ясно. Понятно ☀')))
    else:
        await message.reply('Такого размера нет! Выберите из предложенных.')


async def create_folder(message: types.Message, state=FSMContext):
    if message.text == 'Ясно. Понятно ☀':
        async with state.proxy() as data:
            try:
                os.mkdir('files/{}{}'.format(str(message.from_user.username), message.from_user.id))
                os.mkdir('files/{}{}/{}'.format(str(message.from_user.username), message.from_user.id, data['Услуга']))
                os.mkdir(
                    'files/{}{}/{}/{}'.format(str(message.from_user.username), message.from_user.id, data['Услуга'],
                                              data['Размер']))
            except FileExistsError:
                pass
        await FSMClientPhoto.photos.set()
        await bot.send_message(message.chat.id,
                               'Присылайте мне фото для печати 📎📥\nДля сохранения исходного качества, '
                               'рекомендую отправлять как ФАЙЛ 📄\nПодтвердите отправку кнопкой 📶, ниже',
                               reply_markup=types.
                               ReplyKeyboardMarkup(resize_keyboard=True).
                               add(types.KeyboardButton('Завершить загрузку 📶')))
    else:
        await message.reply('Для продолжения, нажмите на кнопку согласия.')


async def download_image(message: types.Message, state=FSMContext):
    try:
        if message.text != '/start':
            async with state.proxy() as data:
                file_path = 'files/{}{}/{}/{}'.format(str(message.from_user.username), message.from_user.id,
                                                      data['Услуга'],
                                                      data['Размер'])
                if message.photo:
                    img_id = await bot.get_file(message.photo[-1].file_id)
                    foo, extension = img_id.file_path.split('.')
                    saved_image = '{}/{}{}'.format(file_path, img_id.file_id, f'.{extension}')
                    await message.photo[-1].download(f'{saved_image}')
                    # print(message.photo[-1].file_id)

                elif message.document:
                    img_id = await bot.get_file(message.document.file_id)
                    foo, extension = img_id.file_path.split('.')
                    saved_image = '{}/{}{}'.format(file_path, img_id.file_id, f'.{extension}')
                    await message.document.download(f'{saved_image}')

                elif message.text:
                    if message.text == 'Завершить загрузку 📶':
                        file_path_os = os.listdir(path=file_path)
                        if len(file_path_os) > 0:
                            data['Количество'] = len(file_path_os)
                            price, discount = count_price_of_photo(data['Количество'], data['Размер'])
                            data['Скидка'] = str(discount) + ' %'
                            data['Стоимость'] = price
                            await FSMClientPhoto.application.set()
                            await bot.send_message(message.chat.id, f'Принял {data["Количество"]} фото ✍️',
                                                   reply_markup=touch_send_application)
                        else:
                            await FSMClientPhoto.photos.set()
                            await message.reply('Вы не прислали фото.')
                    else:
                        await message.reply('Отправьте мне фото.')
        else:
            await state.finish()
            await client.create_main_bottom(message)
    except:
        await FSMClientPhoto.photos.set()
        await message.reply('Отправьте мне фото.')


def photo_register_handlers(db: Dispatcher):
    db.register_message_handler(main_decorator(get_size_photo), state=None)
    db.register_message_handler(main_decorator(get_agreement), state=FSMClientPhoto.size)
    db.register_message_handler(main_decorator(create_folder), state=FSMClientPhoto.disclaimer)
    db.register_message_handler(download_image, content_types=['photo', 'document', 'text'],
                                state=FSMClientPhoto.photos)
    db.register_message_handler(main_decorator(application), state=FSMClientPhoto.application)
