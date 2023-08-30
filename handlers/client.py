from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import bot
from data_base import data_from_bot
from clientmap import photo, vizit, lists, booklets, fliers, banner, self_adhesive, photo_paper, city_lite, \
    magnet_vinil, plotter_cut, contour_cut, plates, light_box
from handlers.other import main_decorator
from config import CHANNEL_ID_ADMIN


class FSMClientMain(StatesGroup):
    first = State()
    second = State()
    third = State()


async def send_welcome(message: types.Message, state=FSMContext):
    try:
        sticker = data_from_bot.get_content_for_client('sticker_hello')
        await bot.send_sticker(message.chat.id, sticker=sticker[0])
        await bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! '
                                                f'Я здесь что бы помочь вам с вашей задачей. 🐱🤖')
        await bot.send_message(message.chat.id, message.chat.id)
        await create_main_bottom(message)
    except:
        pass


async def create_main_bottom(message: types.Message, state=FSMContext):
    try:
        main_bottom = ['Фотопечать 📸', 'Полиграфия 🖨', 'Сувениры 🛍(СКОРО)', 'Услуги 👩🏻‍🎨(СКОРО)', 'О нас 📝']
        mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mark_up.add(*main_bottom)
        await FSMClientMain.first.set()
        await bot.send_message(message.chat.id, 'Выберите то, что вас интересует:', reply_markup=mark_up)
    except:
        pass


async def create_poly_bottom(message: types.Message, state=FSMContext):
    poly_bottom = ['Флаеры 📄', 'Буклеты 📖', 'Листовки 📃', 'Контурная резка ✂', 'Плоттерная резка 🗡',
                   'Визитки 🪪', 'Широкоформатная печать 📠', 'Световой короб 🗃', 'Календари 📆(СКОРО)',
                   'Таблички 🪧', 'Назад 🔙']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(*poly_bottom[:7])
    mark_up.add(*poly_bottom[7:9])
    mark_up.add(*poly_bottom[9:])
    img = data_from_bot.get_content_for_client('img_poly')
    await bot.send_message(message.chat.id, 'Выберите продукцию:', reply_markup=mark_up)


async def create_large_bottom(message: types.Message, state=FSMContext):
    large_bottom = ['Баннер', 'Самоклейка', 'Фотобумага\n220 гр/м',
                    'CityLite бумага 150г\nДля световой рекламы и постеров', 'Магнит виниловый 0,4мм', 'Назад 🔙']
    mark_up = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark_up.add(*large_bottom[:4])
    mark_up.add(*large_bottom[4:])
    await bot.send_message(message.chat.id, 'Какая продукция Вас интересует?', reply_markup=mark_up)


async def distribution_commands(message: types.Message, state=FSMContext):
    if message.text == 'Фотопечать 📸':
        await photo.get_size_photo(message)
    elif message.text == 'Полиграфия 🖨':
        await FSMClientMain.second.set()
        await create_poly_bottom(message)
    elif message.text == 'Сувениры 🛍(СКОРО)':
        pass
    elif message.text == 'Услуги 👩🏻‍🎨(СКОРО)':
        pass
    elif message.text == 'Услуги 👩🏻‍🎨(СКОРО)':
        pass
    elif message.text == 'О нас 📝':
        await bot.send_message(message.chat.id, 'Мы клевые очень.')
        # await bot.send_message(message.chat.id, 'https://www.youtube.com/watch?v=W4crQPeEIoM&t')
        img = data_from_bot.get_content_for_client('img_about_us')
        mark_up = types.InlineKeyboardMarkup()
        touch_map = types.InlineKeyboardButton('Проложить маршрут', url='https://yandex.ru/maps/35/krasnodar/?ll'
                                                                            '=38.979258%2C45.057761&mode=routes&rtext'
                                                                            '=~45.101166%2C38.980207&rtt=auto&ruri'
                                                                            '=~ymapsbm1%3A%2F%2Forg%3Foid'
                                                                            '%3D1308113072&z=13')
        mark_up.add(touch_map)
        await bot.send_photo(message.chat.id, img[0], 'Мы ждем вас на Дзеринского, 223.', reply_markup=mark_up)


async def distribution_commands_poly(message: types.Message, state=FSMContext):
    if message.text == 'Визитки 🪪':
        await vizit.get_amount_vizit(message)
    elif message.text == 'Флаеры 📄':
        await fliers.get_amount_fliers(message)
    elif message.text == 'Буклеты 📖':
        await booklets.get_amount_booklets(message)
    elif message.text == 'Листовки 📃':
        await lists.get_amount_lists(message)
    elif message.text == 'Широкоформатная печать 📠':
        await FSMClientMain.third.set()
        await create_large_bottom(message)
    elif message.text == 'Календари 📆(СКОРО)':
        await bot.send_message(message.chat.id, 'Скоро календари станут доступны. Не волнуйтесь, до нового года '
                                                'успеем заказать, изготовить, отдать...подарить)')
    elif message.text == 'Плоттерная резка 🗡':
        await plotter_cut.get_color_plotter(message)
    elif message.text == 'Контурная резка ✂':
        await contour_cut.get_size_contour(message)
    elif message.text == 'Таблички 🪧':
        await plates.get_size_plates(message)
    elif message.text == 'Световой короб 🗃':
        await light_box.get_size_light_box(message)
    elif message.text == 'Назад 🔙':
        await state.finish()
        await create_main_bottom(message)


async def distribution_commands_large(message: types.Message, state=FSMContext):
    if message.text == 'Баннер':
        await banner.get_material_type_banner(message)
    elif message.text == 'Самоклейка':
        await self_adhesive.get_material_type_self(message)
    elif message.text == 'Фотобумага\n220 гр/м':
        await photo_paper.get_size_paper(message)
    elif message.text == 'CityLite бумага 150г\nДля световой рекламы и постеров':
        await city_lite.get_size_city(message)
    elif message.text == 'Магнит виниловый 0,4мм':
        await magnet_vinil.get_size_magnet(message)
    elif message.text == 'Назад 🔙':
        await FSMClientMain.second.set()
        await create_poly_bottom(message)
    else:
        await message.reply('Выберите вариант кнопкой!')


async def treatment_callback(call: types.CallbackQuery):
    if call.data == 'Клиент подтвердил оповещение':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Наш адрес: г. Краснодар, ул. Дзержинского, д. 223\nМы работаем:\nПН-ПТ: с '
                                         '9:00 до 18:00\nCБ: c 10:00 до 16:00\nВС: выходной')
        number = data_from_bot.get_number_order(call.message.chat.id)
        await bot.send_message(CHANNEL_ID_ADMIN, f'Клиент подтвердил оповещение. Заказ №{number}')


def client_register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(main_decorator(distribution_commands), state=FSMClientMain.first)
    dp.register_message_handler(main_decorator(distribution_commands_poly), state=FSMClientMain.second)
    dp.register_message_handler(main_decorator(distribution_commands_large), state=FSMClientMain.third)
    dp.register_callback_query_handler(treatment_callback, lambda x: x.data, state=FSMClientMain.first)
    dp.register_callback_query_handler(treatment_callback, lambda x: x.data)
