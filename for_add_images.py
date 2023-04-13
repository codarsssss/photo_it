import sqlite3


def add_items_content(name):
    base = sqlite3.connect('data_base.db')
    cur = base.cursor()
    cur.execute('INSERT INTO data_base_items VALUES(?, ?)', (name, 'CAACAgIAAxkBAAEF8vVjNK685YyWl7nZV7nuZYKKwxL_XAAC3R8AApIiKUmyyRICUiUvWioE', ))
    base.commit()


add_items_content('sticker_light_box')

