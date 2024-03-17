from core.settings import sheet
from core.database import database


def load_user():
    worksheet = sheet.worksheet("user")
    worksheet.clear()
    records = database.get_all_data_user()
    heading = ["user_id", "link", "is admin", "name", "date registration", "scope"]
    worksheet.append_row(heading)
    for i in records:
        worksheet.append_row(i)
