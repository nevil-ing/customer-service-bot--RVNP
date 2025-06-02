# my_scraper/my_scraper/spiders/site_spider.py
import scrapy
from urllib.parse import urlparse

class SiteSpider(scrapy.Spider):
    name = "site_explorer"  

    def __init__(self, site_url="https://rvist.ac.ke/", *args, **kwargs):
        super(SiteSpider, self).__init__(*args, **kwargs)
        if site_url:
            self.start_urls = [site_url]
            parsed_uri = urlparse(site_url)
            self.allowed_domains = [parsed_uri.netloc]
        else:
            self.logger.warning("No 'site_url' argument provided. Spider might not run if start_urls are not defined elsewhere.")
            self.start_urls = []

    def parse(self, response):
        self.logger.info(f"Scraping homepage: {response.url}")

        # --- Extracting General Homepage Data (as before) ---
        page_title_tag = response.css('title::text').get()
        site_brand_title = response.css('p.site-title a::text').get()
        site_brand_description = response.css('p.site-description::text').get()
        contact_phone = response.css('li.quick-call a::text').get()
        contact_email = response.css('li.quick-email a::text').get()
        
        # Yield homepage data
        homepage_data = {
            'type': 'homepage_info',
            'scraped_url': response.url,
            'page_title_tag': page_title_tag.strip() if page_title_tag else None,
            'site_brand': {
                'title': site_brand_title.strip() if site_brand_title else None,
                'description': site_brand_description.strip() if site_brand_description else None,
            },
            'contact_info': {
                'phone': contact_phone.strip() if contact_phone else None,
                'email': contact_email.strip() if contact_email else None,
            },
          
        }
        yield homepage_data

      
        
        department_list_links = response.css('nav#site-navigation ul#primary-menu a[href*="department"]::attr(href)').getall()
        if not department_list_links: # Fallback if the specific selector fails
            department_list_links = response.xpath('//a[contains(translate(text(), "DEPARTMENTS", "departments"), "departments")]/@href').getall()

        if department_list_links:
           
            actual_departments_page_url = None
            for menu_item in response.css('nav#site-navigation ul#primary-menu > li.menu-item'):
                link_text = menu_item.css('a::text').get('').strip().lower()
                link_href = menu_item.css('a::attr(href)').get()
                if link_text == 'departments' and link_href: # Primary check
                    actual_departments_page_url = response.urljoin(link_href)
                    break
            
            if not actual_departments_page_url and department_list_links: # Fallback to first found
                 actual_departments_page_url = response.urljoin(department_list_links[0])


            if actual_departments_page_url:
                self.logger.info(f"Found departments page link: {actual_departments_page_url}")
                yield response.follow(actual_departments_page_url, callback=self.parse_department_list_page)
            else:
                self.logger.warning("Could not find a definitive 'Departments' page link.")
        else:
            self.logger.warning("No links containing 'department' found in main navigation.")


    def parse_department_list_page(self, response):
        self.logger.info(f"Scraping department list page: {response.url}")

        department_page_links = response.css('.entry-content a') 

        if not department_page_links: 
            department_page_links = response.css('section a') 


        found_department_links = False
        for link_tag in department_page_links:
            href = link_tag.css('::attr(href)').get()
            name = link_tag.css('::text').get()

            if href and name:
             
                if 'campus' not in href.lower() and 'event' not in href.lower() and '#' not in href: 
                    self.logger.info(f"Found potential department link: {name.strip()} -> {href}")
                    found_department_links = True
                    yield response.follow(href, 
                                          callback=self.parse_individual_department_page, 
                                          meta={'department_name': name.strip()})
        
        if not found_department_links:
            self.logger.warning(f"No department links found on {response.url}. Check selectors for 'parse_department_list_page'.")


    def parse_individual_department_page(self, response):
        department_name = response.meta.get('department_name', 'Unknown Department')
        self.logger.info(f"Scraping courses for department: {department_name} from {response.url}")

    
        
        courses_found = []

        list_item_courses = response.css('div.entry-content ul li::text').getall() 
        if not list_item_courses: 
            list_item_courses = response.css('article ul li::text').getall()

        for course_name_raw in list_item_courses:
            course_name = course_name_raw.strip()
            if course_name and len(course_name) > 5: # Basic filter for valid course names
                courses_found.append({'course_name': course_name, 'details': 'N/A'})
        
      

        if courses_found:
            yield {
                'type': 'courses_info',
                'department_name': department_name,
                'department_url': response.url,
                'courses': courses_found
            }
        else:
            self.logger.warning(f"No courses found on {response.url} for department {department_name}. Check selectors for 'parse_individual_department_page'.")
            yield { # Yield even if no courses found, to indicate page was processed
                'type': 'courses_info',
                'department_name': department_name,
                'department_url': response.url,
                'courses': [],
                'message': "No courses extracted, selectors might need adjustment."
            }