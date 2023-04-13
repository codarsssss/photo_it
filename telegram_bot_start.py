from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other
from data_base import data_from_bot
from clientmap import photo, vizit, lists, booklets, fliers, banner, self_adhesive, photo_paper, city_lite, \
	magnet_vinil, plotter_cut, contour_cut, plates, light_box


if __name__ == '__main__':
	data_from_bot.start_base()
	client.client_register_handlers(dp)
	admin.admin_register_handlers(dp)
	other.foo_register_handlers(dp)
	photo.photo_register_handlers(dp)
	vizit.vizit_register_handlers(dp)
	lists.lists_register_handlers(dp)
	booklets.booklets_register_handlers(dp)
	fliers.fliers_register_handlers(dp)
	banner.banner_register_handlers(dp)
	self_adhesive.self_register_handlers(dp)
	photo_paper.paper_register_handlers(dp)
	city_lite.city_register_handlers(dp)
	magnet_vinil.magnet_register_handlers(dp)
	plotter_cut.plotter_register_handlers(dp)
	contour_cut.contour_register_handlers(dp)
	plates.plates_register_handlers(dp)
	light_box.light_box_register_handlers(dp)
	executor.start_polling(dp, skip_updates=True)
