import csv
from bs4 import BeautifulSoup
import os

def get_data_from_html(file_path): #загружаем вручную отфильтрованную страницу из фала
    
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден.")
        return []

    # Открываем HTML-файл и читаем его содержимое
    with open(file_path, 'r', encoding='utf-8') as file:
        html_code = file.read()

    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(html_code, 'html.parser')

    # Ищем все div с нужным классом
    company_divs = soup.find_all('div', class_='list-element')
    
    print(f"Найдено {len(company_divs)} компаний в файле {file_path}.")

    company_data = []

    for div in company_divs:
        company_info = {}

        # Название компании — из <a class="list-element__title">
        name_tag = div.find('a', class_='list-element__title')
        if name_tag:
            company_info['name'] = name_tag.get_text(strip=True)

        # ИНН — из <div class="list-element__row-info"> > <span>
        row_info_div = div.find('div', class_='list-element__row-info')
        if row_info_div:
            inn_span = row_info_div.find('span', string=lambda text: text and 'ИНН:' in text)
            if inn_span:
                inn_text = inn_span.get_text(strip=True)
                company_info['inn'] = inn_text.split(':', 1)[1].strip()

        if row_info_div:
            reg_date_span = row_info_div.find('span', string=lambda text: text and 'Дата регистрации:' in text)
            if reg_date_span:
                reg_date_text = reg_date_span.get_text(strip=True)
                company_info['reg_date'] = reg_date_text.split(':', 1)[1].strip()
            else:
                company_info['reg_date'] = ""
        else:
            company_info['reg_date'] = ""

                # Выручка — из <div class="list-element__info-box-item"> > <span> 
        info_box = div.find('div', class_='list-element__info-box')
        if info_box:
            revenue_item = info_box.find('div', class_='list-element__info-box-item')
            if revenue_item:
                revenue_span = revenue_item.find('span', string=lambda text: text and 'Выручка:' in text)
                if revenue_span:
                    # Берем текст следующего элемента (текст с суммой), который находится в теге <div>
                    revenue_text = revenue_span.find_next_sibling().get_text(strip=True)
                    # Убираем лишние пробелы и символы, оставляя только число и "руб."
                    company_info['revenue'] = revenue_text.replace('\xa0', ' ').strip()
                else:
                    company_info['revenue'] = ""
            else:
                company_info['revenue'] = ""
        else:
            company_info['revenue'] = ""

        # Адрес — из <div class="list-element__address">
        address_div = div.find('div', class_='list-element__address')
        if address_div:
            company_info['region'] = address_div.get_text(strip=True)

        
        # Извлекаем ОКВЭД — ищем первый span с классом list-element__text
        okved_span = div.find('span', class_='list-element__text')
        if okved_span:
            company_info['okved_main'] = okved_span.get_text(strip=True)

        # Источник
        company_info['source'] = 'https://www.rusprofile.ru/'

        #Год revenue
        company_info['revenue_year'] = '2025'

        # Добавляем в список
        company_data.append(company_info)

    return company_data

def save_to_csv(data, filename): # Сохраняем данные в csv. файл, 
    
    # Если данных нет, выходим
    if not data:
        print(f"Нет данных для записи в файл {filename}.")
        return

    # Открываем CSV файл для записи данных
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['inn', 'name', 'region', 'okved_main', 'reg_date', 'revenue', 'revenue_year', 'source'], delimiter=';')
        writer.writeheader()  # Записываем заголовки
        writer.writerows(data)  # Записываем данные

    print(f"Данные успешно записаны в файл '{filename}'.")

def main():
    # Указываем имена файлов HTML, скопированных вручную с заранее проставленными фильтрами
    html_files = [
        ('CFO.html'),  
        ('DVFO.html'),
        ('SZFO.html'),
        ('YFO.html'),
        ('SFO.html'),
        ('UFO.html'),
        ('SKFO.html'),
        ('PFO.html')
    ]

    all_company_data = []  # Создаем общий список

    # Обрабатываем каждый файл
    for file_path in html_files:
        company_data = get_data_from_html(file_path)
        if company_data:
            all_company_data.extend(company_data)  # Добавляем данные из текущего файла в общий список

    # Если данных накопилось достаточно, сохраняем в CSV
    if len(all_company_data) >= 200:
        save_to_csv(all_company_data, 'companies.csv')
    else:
        print(f"Не удалось собрать достаточно данных. Всего компаний: {len(all_company_data)}.")

if __name__ == '__main__':
    main()
