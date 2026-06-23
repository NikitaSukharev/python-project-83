from bs4 import BeautifulSoup


def check_h1(soup):
    """Возвращает текст первого тега <h1> или None"""
    h1_tag = soup.find('h1')
    return h1_tag.get_text(strip=True) if h1_tag else None


def check_title(soup):
    """Возвращает текст тега <title> или None"""
    title_tag = soup.find('title')
    return title_tag.get_text(strip=True) if title_tag else None


def check_meta_description(soup):
    """Возвращает содержимое meta[name=description] или None"""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and 'content' in meta_desc.attrs:
        return meta_desc['content'].strip()
    return None


def truncate(text, max_length=200):
    """Обрезает текст до max_length символов с добавлением '...'"""
    if text and len(text) > max_length:
        return text[:max_length] + '...'
    return text


def check_page(html):
    """Анализирует HTML и возвращает словарь с h1, title, description"""
    soup = BeautifulSoup(html, 'html.parser')
    return {
        'h1': truncate(check_h1(soup)),
        'title': truncate(check_title(soup)),
        'description': truncate(check_meta_description(soup)),
    }
