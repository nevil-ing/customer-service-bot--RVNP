# my_scraper/my_scraper/spiders/hef_faq_spider.py
import scrapy
from urllib.parse import urlparse

class HefFaqSpider(scrapy.Spider):
    name = "hef_faqs"  # Unique name for this spider

    def __init__(self, site_url="https://www.hef.co.ke/faqs/", *args, **kwargs):
        super(HefFaqSpider, self).__init__(*args, **kwargs)
        # For this specific spider, the site_url is usually fixed,
        # but we can allow it to be overridden.
        self.start_urls = [site_url]
        parsed_uri = urlparse(site_url)
        self.allowed_domains = [parsed_uri.netloc]
        self.logger.info(f"HefFaqSpider initialized for URL: {site_url}")

    def parse(self, response):
        self.logger.info(f"Scraping {response.url}")

        # 1. Page Title (from <title> tag - Scrapy does this by default, but good to have)
        # The actual title might be in an <h1> or a specific Elementor heading widget
        # For <title> tag:
        html_page_title = response.css('title::text').get()
        
        # Main heading of the FAQ section
        faq_section_title = response.css('div.elementor-element-b88aa82 h2.elementor-heading-title::text').get()

        # 2. Main Navigation Links (Example from the provided sticky header)
        nav_links = []
        # The navigation menu in the sticky header
        for item in response.css('nav.elementor-nav-menu--main ul.elementor-nav-menu li.menu-item a.elementor-item'):
            text = item.css('::text').get()
            href = item.css('::attr(href)').get()
            if text and href:
                nav_links.append({
                    'text': text.strip(),
                    'href': response.urljoin(href.strip())
                })

        # 3. FAQ Items (Questions and Answers)
        # This site has two sets of toggles with slightly different widget IDs but similar structure
        faq_items = []
        # Targeting both toggle widgets (elementor-element-16e6739 and elementor-element-e387d3f)
        for toggle_widget in response.css('div.elementor-widget-toggle'):
            for item in toggle_widget.css('div.elementor-toggle-item'):
                question = item.css('div.elementor-tab-title a.elementor-toggle-title::text').get()
                if not question: # Fallback if <a> tag is not directly there or text is outside
                    question = "".join(item.css('div.elementor-tab-title ::text').getall()).strip()


                # The answer content can have <p> tags or just be text.
                # We select all text nodes within the content div and join them.
                answer_parts = item.css('div.elementor-tab-content ::text').getall()
                answer = ' '.join(part.strip() for part in answer_parts if part.strip())

                if question and answer:
                    faq_items.append({
                        'question': question.strip(),
                        'answer': answer.strip()
                    })
        
        

        yield {
            'scraped_url': response.url,
            'html_page_title': html_page_title.strip() if html_page_title else None,
            'faq_section_main_title': faq_section_title.strip() if faq_section_title else None,
            'navigation_links': nav_links,
            'faq_list': faq_items,
        }