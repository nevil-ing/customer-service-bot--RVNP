

import scrapy
from urllib.parse import urlparse

class SiteExplorerForRagSpider(scrapy.Spider):
    name = "site_explorer_for_rag"

    def __init__(self, site_url=None, *args, **kwargs):
        super(SiteExplorerForRagSpider, self).__init__(*args, **kwargs)
        
        if not site_url:
           
            site_url = "https://rvnp.ac.ke/" 
            self.logger.info(f"No site_url provided, defaulting to {site_url}")

        self.start_urls = [site_url]
        parsed_uri = urlparse(site_url)
        self.allowed_domains = [parsed_uri.netloc]
        self.site_name_meta = parsed_uri.netloc # e.g., 'rvnp.ac.ke'
        self.logger.info(f"SiteExplorerForRagSpider initialized for: {self.start_urls[0]}")


    def parse(self, response):
        self.logger.info(f"Scraping homepage: {response.url} for RAG")
        site_name = self.site_name_meta

        # ---- Homepage 
        
        # 1. HTML Page Title
        page_title_tag = response.css('title::text').get()
        if page_title_tag:
            yield {
                'source_url': response.url,
                'content_type': 'general_info',
                'title': "Website Main Title",
                'text_content': page_title_tag.strip(),
                'metadata': {'site_name': site_name, 'section': 'html_title'}
            }

        # 2. Site Branding (Title and Description)
        site_brand_title_text = response.css('div#site-identity p.site-title a::text').get()
        if site_brand_title_text:
            yield {
                'source_url': response.url,
                'content_type': 'general_info',
                'title': "Institution Name",
                'text_content': site_brand_title_text.strip(),
                'metadata': {'site_name': site_name, 'section': 'brand_title'}
            }
        
        site_brand_description_text = response.css('div#site-identity p.site-description::text').get()
        if site_brand_description_text:
            yield {
                'source_url': response.url,
                'content_type': 'general_info',
                'title': "Institution Tagline/Motto",
                'text_content': site_brand_description_text.strip(),
                'metadata': {'site_name': site_name, 'section': 'brand_description'}
            }

        # 3. Top Bar Contact Information
        contact_phone_text = response.css('div#quick-contact li.quick-call a::text').get()
        contact_email_text = response.css('div#quick-contact li.quick-email a::text').get()
        
        contact_info_parts = []
        if contact_phone_text:
            contact_info_parts.append(f"Phone: {contact_phone_text.strip()}")
        if contact_email_text:
            contact_info_parts.append(f"Email: {contact_email_text.strip()}")
        
        if contact_info_parts:
            yield {
                'source_url': response.url,
                'content_type': 'contact_info',
                'title': f"{site_name.upper()} Primary Contact",
                'text_content': " | ".join(contact_info_parts),
                'metadata': {'site_name': site_name, 'section': 'top_bar_contact'}
            }

        # 4. Top News Snippet in the Top Bar
        top_news_title = response.css('div#quick-contact div.top-news span.top-news-title::text').get()
        top_news_apply_text = response.css('div#quick-contact div.top-news a::text').get()
        top_news_apply_link = response.css('div#quick-contact div.top-news a::attr(href)').get()

        if top_news_title:
            news_content = top_news_title.strip()
            if top_news_apply_text and top_news_apply_link:
                news_content += f" ({top_news_apply_text.strip()}: {response.urljoin(top_news_apply_link)})"
            yield {
                'source_url': response.url,
                'content_type': 'announcement',
                'title': "Homepage Top Announcement",
                'text_content': news_content,
                'metadata': {'site_name': site_name, 'section': 'top_bar_news'}
            }

        # 5. Featured Content Blocks (Admissions, Welcome, About Us summaries)
        for article in response.css('div#featured-content div.inner-wrapper article'):
            feat_title_text = article.css('header.entry-header h2.entry-title a::text').get()
            feat_link = article.css('header.entry-header h2.entry-title a::attr(href)').get()
            
            # Get content, prioritizing direct <p> tags, then any text
            feat_content_p = article.css('div.entry-content div p::text').getall()
            if feat_content_p:
                 feat_content = ' '.join(p.strip() for p in feat_content_p if p.strip())
            else: # Fallback if no <p> or content is outside
                feat_content_all = article.css('div.entry-content ::text').getall()
                feat_content = ' '.join(part.strip() for part in feat_content_all if part.strip())


            if feat_title_text and feat_content:
                yield {
                    'source_url': response.urljoin(feat_link) if feat_link else response.url, 
                    'content_type': 'general_summary', 
                    'title': feat_title_text.strip(),
                    'text_content': feat_content,
                    'metadata': {'site_name': site_name, 'section': 'homepage_featured_content'}
                }
        
  
        departments_page_link = response.css('ul#primary-menu li#menu-item-203 > a::attr(href)').get()
        
        if departments_page_link:
            departments_page_url = response.urljoin(departments_page_link)
            self.logger.info(f"Found main 'Departments' page link: {departments_page_url}")
            yield response.follow(departments_page_url, callback=self.parse_department_list_page)
        else:
            
            general_dept_links = response.xpath('//ul[@id="primary-menu"]//a[contains(translate(text(), "DEPARTMENTS", "departments"), "departments")]/@href').getall()
            if general_dept_links:
                departments_page_url = response.urljoin(general_dept_links[0]) # Take the first one
                self.logger.info(f"Found potential 'Departments' page link (fallback): {departments_page_url}")
                yield response.follow(departments_page_url, callback=self.parse_department_list_page)
            else:
                self.logger.warning(f"Could not find a 'Departments' page link on {response.url}. Course scraping might be incomplete.")

    def parse_department_list_page(self, response):
        self.logger.info(f"Scraping department list page: {response.url}")
        site_name = self.site_name_meta

       
        department_links_on_page = response.css('div.entry-content a') 
      

        found_department_links = False
        for link_tag in department_links_on_page:
            href = link_tag.css('::attr(href)').get()
            name_parts = link_tag.css('::text').getall() # Get all text nodes to capture full name
            name = ' '.join(part.strip() for part in name_parts if part.strip()).strip()

            if href and name and len(name) > 3: 
               
                href_lower = href.lower()
                name_lower = name.lower()
              
                exclude_keywords = ['campus', 'gallery', 'news', 'event', 'contact', 
                                    'tender', 'download', 'login', 'portal', 'apply', 
                                    'about us', 'history', 'policy', 'charter', 'management', 
                                    'principal', 'governor', 'registrar', 'dean', 'complaints', 'faqs',
                                    '#', 'javascript:', 'mailto:', '.pdf', '.doc', '.jpg', '.png']
                
                if not any(kw in href_lower for kw in exclude_keywords) and \
                   not any(kw in name_lower for kw in exclude_keywords):
                    
                    department_page_url = response.urljoin(href)
                    self.logger.info(f"Following to potential department page: {name} -> {department_page_url}")
                    found_department_links = True
                    yield response.follow(department_page_url, 
                                          callback=self.parse_individual_department_page, 
                                          meta={'department_name_from_list': name, 
                                                'department_list_url': response.url})
        
        if not found_department_links:
            self.logger.warning(f"No department links found on {response.url} matching criteria. Check selectors for 'parse_department_list_page'.")
          
            self.logger.info("Attempting fallback: extracting department links from main navigation sub-menu.")
            nav_department_links = response.xpath('//ul[@id="primary-menu"]/li[@id="menu-item-203"]/ul[@class="sub-menu"]/li[not(contains(@class, "menu-item-has-children"))]/a') # Exclude 'Campuses'
            
            nav_found_links = False
            for link_tag in nav_department_links:
                href = link_tag.xpath('./@href').get()
                name = "".join(link_tag.xpath('.//text()').getall()).strip()
                
                if href and name:
                    
                    if "campuses" not in name.lower():
                        department_page_url = response.urljoin(href)
                        self.logger.info(f"Following to department page from nav sub-menu: {name} -> {department_page_url}")
                        nav_found_links = True
                        yield response.follow(department_page_url, 
                                              callback=self.parse_individual_department_page, 
                                              meta={'department_name_from_list': name, 
                                                    'department_list_url': response.url})
            if not nav_found_links:
                 self.logger.error(f"FALLBACK FAILED: Still no department links found on {response.url} even from navigation. Course scraping will be incomplete.")


    def parse_individual_department_page(self, response):
        department_name_from_list = response.meta.get('department_name_from_list', 'Unknown Department')
        site_name = self.site_name_meta

       
        page_h1 = response.css('header.entry-header h1.entry-title::text').get()
        department_name = page_h1.strip() if page_h1 else department_name_from_list
        
        self.logger.info(f"Scraping courses for department: {department_name} from {response.url}")

        desc_paragraphs = response.css('div.entry-content > p') 
        department_description_texts = []
        for p_tag in desc_paragraphs[:3]: 
            p_text = " ".join(p_tag.css('::text').getall()).strip()
            if p_text:
                department_description_texts.append(p_text)
        
        department_description = " ".join(department_description_texts)

        if department_description:
            yield {
                'source_url': response.url,
                'content_type': 'department_description',
                'title': f"About {department_name}",
                'text_content': department_description,
                'metadata': {'site_name': site_name, 'department': department_name}
            }

      
        
        courses_extracted_count = 0
        
        
        course_list_items = response.css('div.entry-content ul li') 
        if not course_list_items: # A more general fallback if the above yields nothing
            course_list_items = response.css('article ul li')


        for li in course_list_items:
            course_full_text_parts = li.css('::text').getall()
            course_full_text = ' '.join(part.strip() for part in course_full_text_parts if part.strip()).strip()
            
            # Basic filtering for meaningful course entries
            if course_full_text and len(course_full_text) > 10 and \
               not any(kw in course_full_text.lower() for kw in ["click here", "download", "admission criteria", "fee structure"]):
                
                # Simple heuristic for splitting name and details
                course_name_part = course_full_text
                course_details_part = ""
                # Common separators
                separators = [" – ", " - ", ": "]
                for sep in separators:
                    if sep in course_full_text:
                        parts = course_full_text.split(sep, 1)
                        course_name_part = parts[0].strip()
                        course_details_part = parts[1].strip() if len(parts) > 1 else ""
                        break # Found a separator

                yield {
                    'source_url': response.url,
                    'content_type': 'course_info',
                    'title': f"Course: {course_name_part}",
                    'text_content': course_full_text,   
                    'metadata': {
                        'site_name': site_name,
                        'department': department_name,
                        'extracted_course_name': course_name_part,
                        'extracted_details': course_details_part
                    }
                }
                courses_extracted_count += 1
   
        if courses_extracted_count == 0:
            self.logger.warning(f"No courses extracted via current list/table selectors for department '{department_name}' at {response.url}. The page content may need specific selectors or might not list courses in a parsable way.")
            # Yield a marker that this page was processed but no specific courses were itemized
            yield {
                'source_url': response.url,
                'content_type': 'department_page_no_courses_itemized',
                'title': f"Department Page Processed: {department_name}",
                'text_content': f"This department page for '{department_name}' was scraped. No individual course items were extracted using current rules. Department description (if available): {department_description}. The page content itself might be useful for RAG if it generally discusses course areas.",
                'metadata': {'site_name': site_name, 'department': department_name}
            }