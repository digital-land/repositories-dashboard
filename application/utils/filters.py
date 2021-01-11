from dateutil import parser


def format_date(date_string):
    date = parser.isoparse(date_string)
    return date.strftime("%c")