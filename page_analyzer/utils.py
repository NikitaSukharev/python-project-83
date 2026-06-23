def format_date(value, fmt='%Y-%m-%d'):
    """Форматирует дату в строку"""
    if value is None:
        return ''
    return value.strftime(fmt)
