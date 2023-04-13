from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from handlers import client
from config import URL_ADMIN
from config import CHANNEL_ID_ADMIN
from data_base import data_from_bot
from handlers.other import main_decorator
from count_price import count_price_of_booklets
from datetime import datetime, timedelta
import os
import os.path


class Main(StatesGroup):
    st_amount = State()
    st_size = State()
    st_type_paper = State()
    st_choice = State()
    st_files = State()
    st_application = State()
    st_design_application = State()

    inline_touch_admin = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton('📝 Написать Администратору 👨‍💻', url=URL_ADMIN))
    touch_send_application = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Отправить '
                                                                                                      'заявку ✅'))

    def __init__(self, name, sizes_photos, amount_poly, sizes_lists, sizes_booklets, sizes_fliers, papers_poly,
                 sizes_banners):
        self.name = name
        self.sizes_photos = sizes_photos  # ['10х15', '15х21', '21х30', '30х40']
        self.amount_poly = amount_poly  # ['500шт', '1000шт', '2000шт', '2500шт', '3000шт', '4000шт', '5000шт', '10000шт']
        self.sizes_lists = sizes_lists  # ['А7', 'А6', 'А5', 'А4']
        self.sizes_booklets = sizes_booklets  # ['А6 > А7', 'А5 > А6', 'А4 > А5', 'А3 > А4', 'Евробуклет 210х198 > 210х99']
        self.sizes_fliers = sizes_fliers  # ['Еврофлаер 210х99', 'Мини флаер 150х90']
        self.papers_poly = papers_poly  # ['115', '130', '300', '80', '90', '200']
        self.sizes_banners = sizes_banners  # ['Баннер ламинированный 440 гр/м', 'Баннерная сетка 360 гр/м']

    async def get_amount(self, message: types.Message, state=FSMContext):
        amount_bottom = self.amount_poly
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mark_up.add(*amount_bottom)
        await Main.st_amount.set()
        sticker = data_from_bot.get_content_for_client('sticker_booklets')
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, 'Выберите тираж:', reply_markup=mark_up)

    async def get_size(self, message: types.Message, state=FSMContext):
        if message.text.split()[0] in self.amount_poly:
            async with state.proxy() as data:
                data['Услуга'] = self.name
                data['Тираж'] = message.text.split()[0]
            size_bottom = ['А6 > А7', 'А4 > А5', 'А3 > А4', 'А5 > А6', 'Евробуклет 210х198 > 210х99']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
            mark_up.add(*size_bottom[:4])
            mark_up.add(size_bottom[4])
            await Main.st_size.set()
            await bot.send_message(message.chat.id, 'Выберите размер', reply_markup=mark_up)
        else:
            await message.reply('Выберите тираж кнопкой')

    async def get_paper(self, message: types.Message, state=FSMContext):
        if message.text in self.sizes_booklets:
            if message.text == 'Евробуклет 210х198 > 210х99':
                sticker = data_from_bot.get_content_for_client('sticker_eurobooklets')
                await bot.send_sticker(message.chat.id, sticker=sticker[0])
            async with state.proxy() as data:
                data['Размер'] = message.text
            paper_bottom = ['Мелованная бумага\n115 г/м2', 'Мелованная бумага\n130 г/м2 ⭐',
                            'Мелованный картон\n300 г/м2',
                            'Офсетная бумага\n80 г/м2', 'Мелованная бумага\n90 г/м2', 'Мелованная бумага\n200 г/м2']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            mark_up.add(*paper_bottom)
            await Main.st_type_paper.set()
            await bot.send_message(message.chat.id, 'Выберите плотность бумаги:', reply_markup=mark_up)

    async def get_choice_design(self, message: types.Message, state=FSMContext):
        if message.text.split()[2] in self.papers_poly:
            async with state.proxy() as data:
                data['Бумага'] = message.text.split('⭐')[0]
                papers = {'500шт': 0, '1000шт': 1, '2500шт': 2, '5000шт': 3, '10000шт': 4}
                data['Стоимость'] = count_price_of_booklets(papers[data['Тираж']], data['Размер'].split()[0],
                                                            int(data['Бумага'].split()[2]))
            choice_bottom = ['Всё в наличии. Перейди к оформлению ✅', 'Заказать макет у дизайнера 👩🏻‍🎨']
            mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            mark_up.add(*choice_bottom)
            sticker = data_from_bot.get_content_for_client('sticker_design')
            await Main.st_choice.set()
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
            await bot.send_message(message.chat.id, f'Согласно выбранным параметрам, стоимость составит:\n'
                                                    f'*{data["Стоимость"]}*\n\nУ вас есть дизайн макет?',
                                   reply_markup=mark_up, parse_mode='Markdown')
        else:
            await message.reply('Выберите плотность на клавиатуре!')

    async def get_design_layout(self, message: types.Message, state=FSMContext):
        async with state.proxy() as data:
            if message.text == 'Заказать макет у дизайнера 👩🏻‍🎨':
                data['Дизайнер'] = ''
                await Main.st_design_application.set()
                await bot.send_message(message.chat.id,
                                       'Стоимость одностороннего макета 700р, для двухсторонего 1200р.\n'
                                       'Опишите что бы вы хотели.',
                                       reply_markup=Main.touch_send_application)
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
                await Main.st_files.set()
                await bot.send_message(message.chat.id, 'Пришлите файл. Рекомендавано Расширения TIFF, CMD...',
                                       reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).
                                       add(types.KeyboardButton('Завершить загрузку 📶')))

    async def get_layout_files(self, message: types.Message, state=FSMContext):
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
                                await Main.st_application.set()
                                await bot.send_message(message.chat.id,
                                                       f'Заявка сформиравана. Производство занимает 3-5 рабочих дней. '
                                                       f'Максимальная дата выдачи: {ready_date.strftime("%d.%m")}\n'
                                                       f'Отправить?', reply_markup=Main.touch_send_application)
                            else:
                                await message.reply('Отправьте макет!')
            else:
                await state.finish()
                await client.create_main_bottom(message)
        except:
            await Main.st_files.set()
            await message.reply('Отправьте мне макет.')

    async def application(self, message: types.Message, state=FSMContext):
        async with state.proxy() as data:
            today = datetime.today()
            time_now = datetime.now()
            data_from_bot.add_content(today.strftime('%d.%m.%y'), time_now.strftime('%H:%M'), str(message.from_user.id),
                                      '@' + str(message.from_user.username),
                                      data['Услуга'], data['Стоимость'])
            mess_text = ''
            for key, value in data.items():
                mess_text += '{} - {}\n'.format(key, value)
            sticker = data_from_bot.get_content_for_client('sticker_admin')
            await bot.send_sticker(message.chat.id, sticker=sticker[0])
            await bot.send_message(message.chat.id, f'Ваша заявка: \n{mess_text}',
                                   reply_markup=types.ReplyKeyboardRemove())
            if message.from_user.username is not None:
                await bot.send_message(message.chat.id, 'Я уже передал Вашу заявку администратору. '
                                                        'Он скоро с Вами свяжется! \n\nЕсли дело срочное, Вы можете '
                                                        'самостоятельно написать ему 👨‍💻',
                                       reply_markup=Main.inline_touch_admin)
            else:
                await bot.send_message(message.chat.id,
                                       'Пожалуйста, свяжитесь с администратором нажатием этой кнопки ⬇️',
                                       reply_markup=Main.inline_touch_admin)
                await bot.send_message(message.chat.id, 'Что бы мы могли автоматичесски связываться в будущем,'
                                                        ' задайте себе имя пользователя (ссылку) в настройках '
                                                        'Телеграмм 📌')
            mess_text += 'Клиент - @{}\nИмя - {}'.format(str(message.from_user.username), message.from_user.first_name)
            await bot.send_message(CHANNEL_ID_ADMIN, mess_text)
            await state.finish()
            await client.create_main_bottom(message)

    async def design_application(self, message: types.Message, state=FSMContext):
        async with state.proxy() as data:
            if message.text != 'Отправить заявку ✅':
                data['Дизайнер'] += message.text + '\n'
            else:
                sticker = data_from_bot.get_content_for_client('sticker_admin')
                await bot.send_sticker(message.chat.id, sticker=sticker[0])
                if message.from_user.username is not None:
                    await bot.send_message(message.chat.id, 'Я уже передал ваши пожелания Дизайнеру, скоро с Вами '
                                                            'свяжется! \n\n'
                                                            'Также Вы можете самостоятельно связаться с '
                                                            'Администратором.\n\nУспехов!',
                                           reply_markup=Main.inline_touch_admin)
                else:
                    await bot.send_message(message.chat.id,
                                           'Пожалуйста, свяжитесь с Администратором нажатием кнопки ниже.\n\nУспехов!',
                                           reply_markup=Main.inline_touch_admin)
                mess_text = f'Для Дизайнера\nУслуга: {data["Услуга"]}\nТираж: {data["Тираж"]}\n\nОписание заявки:' \
                            f'\n{data["Дизайнер"]}'
                mess_text += '\nКлиент - @{}\nИмя - {}'.format(str(message.from_user.username),
                                                               message.from_user.first_name)
                await bot.send_message(CHANNEL_ID_ADMIN, mess_text)
                await state.finish()
                await client.create_main_bottom(message)

    def booklets_register_handlers(dp: Dispatcher):
        dp.register_message_handler(Main.get_amount, state=None)
        dp.register_message_handler(Main.get_size, state=Main.st_amount)
        dp.register_message_handler(Main.get_paper, state=Main.st_size)
        dp.register_message_handler(main_decorator(Main.get_choice_design), state=Main.st_type_paper)
        dp.register_message_handler(main_decorator(Main.get_design_layout), state=Main.st_choice)
        dp.register_message_handler(Main.get_layout_files, content_types=['document', 'text'],
                                    state=Main.st_files)
        dp.register_message_handler(main_decorator(Main.design_application),
                                    state=Main.st_design_application)
        dp.register_message_handler(main_decorator(Main.application), state=Main.st_application)


class Booklets(Main):
    def __init__(self, name, amount_poly, sizes_booklets, papers_poly):
        self.name = name
        self.amount_poly = amount_poly
        self.sizes_booklets = sizes_booklets
        self.papers_poly = papers_poly
