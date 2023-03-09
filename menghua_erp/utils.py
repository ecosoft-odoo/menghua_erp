from num2words import num2words
from datetime import datetime

def amount_in_bahttext(amount):
    return num2words(amount, to="currency", lang="th")

def to_thai_date(date_str):
    d = datetime.strptime(date_str, '%Y-%m-%d')
    date = d.strftime("%-d")
    month = d.strftime("%B")
    year = d.strftime("%Y")
    thai_month = {
        "January": "มกราคม",
        "February": "กุมภาพันธ์",
        "March": "มีนาคม",
        "April": "เมษายน",
        "May": "พฤษภาคม",
        "June": "มิถุนายน",
        "July": "กรกฎาคม",
        "August": "สิงหาคม",
        "September": "กันยายน",
        "October": "ตุลาคม",
        "November": "พฤศจิกายน",
        "December": "ธันวาคม",
    }
    return "วันที่ %s %s %s" % (date, thai_month.get(month), int(year) + 543)