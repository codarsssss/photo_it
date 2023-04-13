from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.types.message import ContentType
from create_bot import bot, dp
from handlers import client, other
from config import PAY_TOKEN, CHANNEL_ID_ADMIN
from data_base import data_from_bot


info = {}


# photo_url='https://s00.yaplakal.com/pics/pics_original/2/5/7/16011752.jpg', photo_size=512, photo_height=250,
# photo_width=250,
async def pay_order(message: Message, data):
    info[str(message.chat.id)] = data[0]
    order = [LabeledPrice(label=data[5], amount=int(data[6].split()[0]) * 100)]
    await bot.send_invoice(message.chat.id, title=data[5],
                           description='Не переживайте, всё будет окей.',
                           provider_token=PAY_TOKEN,
                           currency='rub',
                           need_name=True,
                           need_phone_number=True,
                           prices=order,
                           payload='same')


@dp.pre_checkout_query_handler(lambda x: True)
async def check_progress(checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def answer_after_buy(message: Message):
    data_from_bot.replace_payment_status(info[str(message.chat.id)])
    await bot.send_message(CHANNEL_ID_ADMIN, f'№{info[str(message.chat.id)]} - ОПЛАЧЕН')
    del info[str(message.chat.id)]
    if message.from_user.username is not None:
        await bot.send_message(message.chat.id, '*Оплата прошла успешно!* Я уже передал Вашу заявку администратору. '
                                                'Он скоро с Вами свяжется! \n\nЕсли дело срочное, Вы можете '
                                                'самостоятельно написать ему 👨‍💻',
                               reply_markup=other.inline_touch_admin, parse_mode='Markdown')
    else:
        await bot.send_message(message.chat.id, '*Оплата прошла успешно!* Пожалуйста, свяжитесь с администратором '
                                                'нажатием этой кнопки ⬇', reply_markup=other.inline_touch_admin, parse_mode='Markdown')
        await bot.send_message(message.chat.id, 'Что бы мы могли автоматичесски связываться в будущем, '
                                                'задайте себе имя пользователя (ссылку) в настройках '
                                                'Телеграмм 📌')

    await client.create_main_bottom(message)
