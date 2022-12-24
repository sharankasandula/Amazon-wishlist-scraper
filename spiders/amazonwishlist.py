import scrapy
import re
import csv
from datetime import datetime


class AmazonWishlistSpider(scrapy.Spider):
    BASE_URL = 'https://www.amazon.com'
    name = 'amazonwishlist'
    allowed_domains = ['www.amazon.com']

    def __init__(self, uri, scraped_data, **kwargs):
        self.scraped_data = scraped_data
        self.start_urls = [uri]

        domain = re.sub(r'(http|https)?://', '', uri)
        self.allowed_domains.append(domain)

        super().__init__(**kwargs)

    def parse(self, response):
        page_items = response.css(".g-item-sortable")

        for item in page_items:
            id = item.css('li::attr(data-itemid)').extract_first()
            title = item.css('#itemName_'+id + "::text").extract_first()
            link = item.css('#itemName_'+id + "::attr(href)").extract_first()
            img = item.css('#itemImage_'+id).css('img::attr(src)').extract_first()
            price = item.css('#itemPrice_'+id).css('span::text').get() if item.css('#itemPrice_'+id).css('span::text').get() != None else 'NA'
            

            wl_response = {
                'id': id,
                'title': title.strip(),
                'link': 'https://www.amazon.in' + link,
                'price': price[1:],
                'timestamp': datetime.datetime.now()
            }
            
            results_csv = open('wl_scrape_data.csv', 'a')
            csv_writer = csv.writer(results_csv)
            
            # csv_writer.writerow(wl_response.keys())
            csv_writer.writerow(wl_response.values())
            results_csv.close()

            self.scraped_data.append(wl_response)
            yield wl_response

        # manage "infinite scrolldown"
        has_next = response.css('#sort-by-price-next-batch-lek::attr(value)').extract_first()
        if has_next:
            lek_uri = response.css('#sort-by-price-load-more-items-url-next-batch::attr(value)').extract_first()
            next_page = self.BASE_URL + lek_uri
            yield scrapy.Request(next_page)

