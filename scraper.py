from bs4 import BeautifulSoup
from urllib.request import urlopen

url = 'https://rvist.ac.ke/'
page = urlopen(url)
html = page.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
""""
def scrape_courses():
    courses = []
    courses_section = soup.find('li', id='menu-item-1637')  
    if courses_section:
        sub_menu_items = courses_section.find('ul', class_='sub-menu')
        if sub_menu_items:
            course_category_links = sub_menu_items.find_all('a')
            for link in course_category_links:
                course_category_title = link.text.strip()
                course_category_url = link['href']
                
                page_courses = urlopen(course_category_url)
                html_courses = page_courses.read().decode('utf-8')
                soup_courses = BeautifulSoup(html_courses, 'html.parser')

                courses_title_tag = soup_courses.find('h1', class_='entry-title')
                if courses_title_tag:
                    course_title = courses_title_tag.text.strip()

                courses_list = soup_courses.find_all('div', class_='wp-block-file') 
                for div in courses_list:
                    course_name = div.find('a').text.strip()
                    course_info_download_link = div.find('a', class_='wp-block-file__button')['href']
                    courses.append({
                        'course_name': course_name,
                        'download_link': course_info_download_link
                    })
    return courses

def scrape_online_application():
    online_application = {}
    online_application_section = soup.find('li', id='menu-item-1631')
    if online_application_section:
        application_link = online_application_section.find('a')
        online_application = {
            'title': application_link.text.strip(),
            'url': application_link['href']
        }
    return online_application

def scrape_manual_application():
    manual_application = {}
    manual_application_section = soup.find('li', id='menu-item-1738') 
    if manual_application_section:
        application_link = manual_application_section.find('a')
        manual_application = {
            'title': application_link.text.strip(),
            'url': application_link['href']
        }
    return manual_application

def scrape_fee_requirements():
    fee_requirements = {}
    fee_requirements_section = soup.find('li', id='menu-item-1632') 
    if fee_requirements_section:
        fee_req_link = fee_requirements_section.find('a')
        fee_requirements = {
            'title': fee_req_link.text.strip(),
            'url': fee_req_link['href']
        }
    return fee_requirements

def scrape_tenders():
    tenders = []
    tenders_section = soup.find('li', id='menu-item-1184')
    if tenders_section:
        tenders_link = tenders_section.find('a')
        tenders_url = tenders_link['href']

        page_tenders = urlopen(tenders_url)
        html_tenders = page_tenders.read().decode('utf-8')
        soup_tenders = BeautifulSoup(html_tenders, 'html.parser')
    
        tenders_list = soup_tenders.find_all('p')
        for paragraph in tenders_list:
            tender_link = paragraph.find('a')
            if tender_link:
                tender_name = tender_link.text.strip()
                tender_url = tender_link['href']
                tenders.append({
                    'tender_name': tender_name,
                    'tender_url': tender_url
                })
    return tenders

def scrape_contact_data():
    contact_info = {}
    contact_information_section = soup.find('li', id='menu-item-112')
    if contact_information_section:
        contact_link = contact_information_section.find('a')
        contact_url = contact_link['href']
    
        page_contact = urlopen(contact_url)
        html_contact = page_contact.read().decode('utf-8')
        soup_contact = BeautifulSoup(html_contact, 'html.parser')
    
        contact_list = soup_contact.find_all('p')
        for paragraph in contact_list:
            contact_detail = paragraph.find('strong')
            if contact_detail:
                key = paragraph.get_text().split(':')[0].strip()
                value = contact_detail.text.strip()
                contact_info[key] = value
    return contact_info

def scrape_hostel_booking():
    hostel_booking = {}
    hostel_booking_section = soup.find('li', id='menu-item-350')
    if hostel_booking_section:
        hostel_booking_link = hostel_booking_section.find('a')
        hostel_booking_url = hostel_booking_link['href']

        page_hostel = urlopen(hostel_booking_url)
        html_hostel = page_hostel.read().decode('utf-8')
        soup_hostel = BeautifulSoup(html_hostel, 'html.parser')

        hostel_title_tag = soup_hostel.find('h1', class_='entry-title')
        if hostel_title_tag:
            hostel_booking['title'] = hostel_title_tag.text.strip()
        
        content_paragraphs = soup_hostel.find_all('p')
        ordered_list = soup_hostel.find('ol')

        hostel_booking['details'] = [p.get_text().strip() for p in content_paragraphs]
        if ordered_list:
            hostel_booking['list_items'] = [li.get_text().strip() for li in ordered_list.find_all('li')]
    return hostel_booking
"""