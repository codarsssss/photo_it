from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from count_price import count_price_of_lists
from create_bot import bot
from data_base import data_from_bot
from handlers import client
from handlers.other import main_decorator, list_with_amount_for_poly, list_with_sizes_for_lists, \
    list_with_papers_for_poly, touch_send_application, design_application, application
from datetime import datetime, timedelta
import os
import os.path


class FSMClientLists(StatesGroup):
    amount = State()
    size = State()
    type_paper = State()
    choice = State()
    files = State()
    application = State()
    design_application = State()


async def get_amount_lists(message: types.Message, state=FSMContext):
    amount_bottom = ['500шт', '1000шт ⭐', '2500шт', '5000шт', '10000шт']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(*amount_bottom)
    await FSMClientLists.amount.set()
    sticker = data_from_bot.get_content_for_client('sticker_lists')
    await bot.send_sticker(message.chat.id, sticker=sticker[0])
    await bot.send_message(message.chat.id, 'Выберите тираж:', reply_markup=mark_up)


async def get_size_lists(message: types.Message, state=FSMContext):
    if message.text.split()[0] in list_with_amount_for_poly:
        async with state.proxy() as data:
            data['Услуга'] = 'Листовки'
            data['Тираж'] = message.text.split()[0]
        size_bottom = ['А7', 'А5', 'А4', 'А6 ⭐']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mark_up.add(*size_bottom)
        await FSMClientLists.size.set()
        await bot.send_message(message.chat.id, 'Выберите размер', reply_markup=mark_up)
    else:
        await message.reply('Выберите тираж кнопкой')


async def get_paper_lists(message: types.Message, state=FSMContext):
    if message.text.split()[0] in list_with_sizes_for_lists:
        async with state.proxy() as data:
            data['Размер'] = message.text.split()[0]
        paper_bottom = ['Мелованная бумага\n115 г/м2', 'Мелованная бумага\n130 г/м2 ⭐', 'Мелованный картон\n300 г/м2',
                        'Офсетная бумага\n80 г/м2', 'Мелованная бумага\n90 г/м2', 'Мелованная бумага\n200 г/м2']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        mark_up.add(*paper_bottom)
        await FSMClientLists.type_paper.set()
        await bot.send_message(message.chat.id, 'Выберите плотность бумаги:', reply_markup=mark_up)


async def get_choice_design(message: types.Message, state=FSMContext):
    if message.text.split()[2] in list_with_papers_for_poly:
        async with state.proxy() as data:
            data['Бумага'] = message.text.split('⭐')[0]
            papers = {'500шт': 0, '1000шт': 1, '2500шт': 2, '5000шт': 3, '10000шт': 4}
            data['Стоимость'] = count_price_of_lists(papers[data['Тираж']], data['Размер'].split()[0],
                                                     int(data['Бумага'].split()[2]))
        choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        mark_up.add(*choice_bottom)
        sticker = data_from_bot.get_content_for_client('sticker_design')
        await FSMClientLists.choice.set()
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, f'Согласно выбранным параметрам, стоимость составит:\n'
                                                f'*{data["Стоимость"]}*\n\nУ вас есть дизайн макет?',
                               reply_markup=mark_up, parse_mode='Markdown')
    else:
        await message.reply('Выберите плотность на клавиатуре!')


async def get_design_layout(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        if message.text == 'Заказать макет у дизайнера 👩🏻‍🎨':
            data['Дизайнер'] = ''
            await FSMClientLists.design_application.set()
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
            await FSMClientLists.files.set()
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
                            await FSMClientLists.application.set()
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
        await FSMClientLists.files.set()
        await message.reply('Отправьте мне макет.')


def lists_register_handlers(dp: Dispatcher):
    dp.register_message_handler(main_decorator(get_amount_lists), state=None)
    dp.register_message_handler(main_decorator(get_size_lists), state=FSMClientLists.amount)
    dp.register_message_handler(main_decorator(get_paper_lists), state=FSMClientLists.size)
    dp.register_message_handler(main_decorator(get_choice_design), state=FSMClientLists.type_paper)
    dp.register_message_handler(main_decorator(get_design_layout), state=FSMClientLists.choice)
    dp.register_message_handler(get_layout_files, content_types=['document', 'text'], state=FSMClientLists.files)
    dp.register_message_handler(main_decorator(design_application), state=FSMClientLists.design_application)
    dp.register_message_handler(main_decorator(application), state=FSMClientLists.application)
