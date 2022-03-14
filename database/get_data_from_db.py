from database.models import ThemeTable
import random


async def get_data_from_db():
    all_themes = ThemeTable.get_all_theme()
    random.shuffle(all_themes)
    return all_themes

