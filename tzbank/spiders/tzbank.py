import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tzbank.items import Article


class tzbankSpider(scrapy.Spider):
    name = 'tzbank'
    start_urls = ['http://www.tzbank.com/news.jsp']

    def parse(self, response):
        articles = response.xpath('//div[@class="news_list"]/ul/li')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./a/span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[text()="下一页"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="detail_h3"]/text()[2]').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="edit_content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
