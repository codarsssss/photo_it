def count_price_of_photo(number, size):
    cost = 0
    if number >= 250:
        cost = 20 * number
    elif number >= 200:
        cost = 22 * number
    elif number >= 150:
        cost = 24 * number
    elif number >= 100:
        cost = 26 * number
    elif number >= 50:
        cost = 28 * number
    else:
        cost = 30 * number

    def get_inf_cost_base(num):
        if num >= 250:
            sale = 20
        elif num >= 200:
            sale = 22
        elif num >= 150:
            sale = 24
        elif num >= 100:
            sale = 26
        elif num >= 50:
            sale = 28
        else:
            sale = 30
        percent = 100 - (sale / 30 * 100)
        return percent

    if size == '10х15':
        discount = get_inf_cost_base(number)
        return str(cost) + ' руб.', round(discount, 2)
    elif size == '15х21':
        discount = get_inf_cost_base(number)
        return str(cost * 2) + ' руб.', round(discount, 2)
    elif size == '21х30':
        discount = get_inf_cost_base(number)
        return str(cost * 4) + ' руб.', round(discount, 2)
    elif size == '30х40':
        return str(490 * number) + ' руб.', 0


def count_price_of_vizit(number):
    price = {'500шт': '1200 руб.',
             '1000шт ⭐': '1400 руб.',
             '2000шт': '2100 руб.',
             '3000шт': '3400 руб.',
             '4000шт': '4100 руб.',
             '5000шт': '5400 руб.',
             '10000шт': '8100 руб.'}
    return price[number]


def count_price_of_lists(amount, size, paper):
    if size == 'А7':
        dict_a7 = {115: [1350, 1500, 2900, 4600, 7000],
                   130: [1400, 1550, 2950, 4650, 7100],
                   300: [2600, 2900, 5300, 10550, 18650],
                   80: [1350, 1500, 2800, 4350, 6550],
                   90: [1400, 1550, 2950, 4600, 7050],
                   200: [1750, 1900, 3700, 6050, 9800]}
        return str(dict_a7[paper][amount]) + ' руб.'

    elif size == 'А6':
        dict_a6 = {115: [1650, 1850, 3500, 5650, 9050],
                   130: [1750, 1950, 3600, 5750, 9200],
                   300: [3750, 4150, 9300, 15600, 27950],
                   80: [1750, 1950, 3350, 5250, 8300],
                   90: [1800, 2000, 3600, 5700, 9100],
                   200: [2300, 2550, 4800, 8050, 13650]}
        return str(dict_a6[paper][amount]) + ' руб.'

    elif size == 'А5':
        dict_a5 = {115: [2450, 2700, 5050, 8300, 14050],
                   130: [2550, 2850, 5200, 8450, 14350],
                   300: [6600, 7300, 17950, 28200, 51900],
                   80: [2450, 2700, 4650, 7500, 12550],
                   90: [2600, 2900, 5100, 8350, 14150],
                   200: [3650, 4100, 7600, 13150, 23250]}
        return str(dict_a5[paper][amount]) + ' руб.'

    elif size == 'А4':
        dict_a4 = {115: [3950, 4400, 7750, 12850, 22750],
                   130: [4250, 4700, 8450, 13900, 24750],
                   300: [12250, 13600, 24900, 53400, 99750],
                   80: [4000, 4450, 7350, 12000, 21100],
                   90: [4300, 4800, 8200, 13650, 24300],
                   200: [6450, 7150, 13250, 23300, 42550]}
        return str(dict_a4[paper][amount]) + ' руб.'


def count_price_of_booklets(amount, size, paper):
    if size == 'А6':
        dict_a6 = {115: [2100, 2350, 4300, 6850, 11050],
                   130: [2200, 2450, 4400, 6950, 11100],
                   300: [3950, 5000, 11100, 19450, 35500],
                   80: [2050, 2300, 4000, 6300, 10000],
                   90: [2150, 2400, 4250, 6800, 10950],
                   200: [3000, 3350, 6700, 11750, 20850]}
        return str(dict_a6[paper][amount]) + ' руб.'

    elif size == 'А5':
        dict_a5 = {115: [2900, 3200, 5850, 9450, 16200],
                   130: [3100, 3450, 5950, 9600, 16300],
                   300: [7350, 8150, 20550, 32050, 59450],
                   80: [2850, 3150, 5350, 8550, 14300],
                   90: [3000, 3350, 5800, 9450, 16050],
                   200: [4400, 4900, 9500, 16800, 30450]}
        return str(dict_a5[paper][amount]) + ' руб.'

    elif size == 'А4':
        dict_a4 = {115: [4450, 4950, 8900, 14900, 26350],
                   130: [4900, 5450, 9200, 15100, 26750],
                   300: [13050, 14500, 36900, 55600, 103750],
                   80: [4450, 4950, 8550, 14500, 26050],
                   90: [4750, 5250, 8950, 14850, 26300],
                   200: [7200, 7950, 15100, 26950, 49750]}
        return str(dict_a4[paper][amount]) + ' руб.'

    elif size == 'А3':
        dict_a3 = {115: [7650, 8450, 15200, 25950, 47350],
                   130: [8550, 9500, 15850, 26450, 48350],
                   300: [24400, 27100, 68850, 106050, 199500],
                   80: [7550, 8400, 13500, 22350, 40550],
                   90: [8250, 9150, 15350, 25950, 47450],
                   200: [13500, 15000, 26900, 49950, 93350]}
        return str(dict_a3[paper][amount]) + ' руб.'

    elif size == 'Евробуклет':
        dict_euro = {115: [3400, 3800, 6850, 11350, 19550],
                     130: [3700, 4100, 7050, 11450, 19800],
                     300: [9700, 10800, 26300, 40250, 74250],
                     80: [3350, 3750, 6250, 10050, 17200],
                     90: [3600, 4000, 6850, 11250, 19500],
                     200: [5800, 6400, 11500, 19950, 35800]}
        return str(dict_euro[paper][amount]) + ' руб.'


def count_price_of_fliers(amount, size, paper):
    if size == 'Еврофлаер':
        dict_euro = {115: [1800, 2000, 3850, 6200, 10100],
                     130: [2000, 2250, 4150, 6650, 10900],
                     300: [4700, 5200, 12300, 19800, 35900],
                     80: [1950, 2150, 3800, 6000, 9700],
                     90: [2050, 2250, 4050, 6550, 10750],
                     200: [2750, 3050, 5750, 9750, 16850]}
        return str(dict_euro[paper][amount]) + ' руб.'

    elif size == 'Мини':
        dict_mini = {115: [1650, 1850, 3500, 5650, 9050],
                     130: [1750, 1950, 3550, 5700, 9200],
                     300: [3750, 4150, 9500, 15600, 27950],
                     80: [1700, 1850, 3350, 5250, 8300],
                     90: [1800, 2000, 3650, 5750, 9250],
                     200: [2300, 2550, 4800, 8050, 13650]}
        return str(dict_mini[paper][amount]) + ' руб.'


def count_price_of_banner(x, y, material, choice):
    s = (x * y) / 1000
    p = (x + y) * 2

    if material == 'Баннер':
        price_per_square = 65
    else:
        price_per_square = 55

    print_cost = s * price_per_square

    if choice == 'Да':
        grommets = (p / 20) * 30
        edge = p * 120 / 100
        plus = grommets + edge
    else:
        plus = 0

    if (print_cost + plus) < 800:
        return str(800) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost + plus)) + ' руб.'


def count_price_of_self(x, y, material):
    s = (x * y) / 1000

    if material == 'Самоклейка':
        price_per_square = 80
    else:
        price_per_square = 90

    print_cost = s * price_per_square

    if print_cost < 800:
        return str(800) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_paper(x, y):
    s = (x * y) / 1000
    print_cost = s * 90

    if print_cost < 850:
        return str(850) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_city(x, y):
    s = (x * y) / 1000
    print_cost = s * 65

    if print_cost < 700:
        return str(700) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_magnet(x, y):
    s = (x * y) / 1000
    print_cost = s * 80

    if print_cost < 700:
        return str(700) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_plotter(x, y):
    s = (x * y) / 1000
    print_cost = s * 120

    if print_cost < 800:
        return str(800) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_contour(x, y, amount):
    s = (x * y) / 100000
    s *= amount
    print_cost = s * 170

    if print_cost < 2100:
        return str(2100) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_plates(x, y):
    s = (x * y) / 1000
    print_cost = s * 250

    if print_cost < 600:
        return str(600) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'


def count_price_of_light_box(x, y):
    s = (x * y) / 1000
    print_cost = s * 1300

    if print_cost < 13000:
        return str(13000) + ' руб. Это минимальная стоимость заказа!'
    else:
        return str(int(print_cost)) + ' руб.'
