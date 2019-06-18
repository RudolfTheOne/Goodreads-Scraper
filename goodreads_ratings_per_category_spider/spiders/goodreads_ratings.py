import scrapy
import re
from scrapy.http import Request
from collections import OrderedDict


URL = "https://www.goodreads.com/shelf/show/conspiracy"
count = 50
EMAIL = "marcin.szymczak@gmail.com"

class goodreads_book_attributes_combined(scrapy.Item):
     title = scrapy.Field()
     author = scrapy.Field()
     booklink = scrapy.Field()
     ratingscount = scrapy.Field()
     rating = scrapy.Field()
     genre1 = scrapy.Field()
     genre2 = scrapy.Field()
     genre3 = scrapy.Field()
     genre4 = scrapy.Field()

class RatingsSpider(scrapy.Spider):
    name = "goodreads_ratings"
    allowed_domains = ["goodreads.com"]
    start_urls = ['https://www.goodreads.com', ]


    def parse(self, response):

        token = response.css('input[name=authenticity_token]::attr(value)').get()
        return scrapy.FormRequest.from_response(response, formdata={"user[email]":EMAIL, "user[password]":self.password, "authenticity_token":token, "action":"https://www.goodreads.com/user/sign_in?source=home"}, method="POST", callback=self.after_login)

    def after_login(self, response):
        # check login succeed before going on
        if b"recognize that email" in response.body:
            print ("################ ERROR ##################")
            return
        else:
            #authenticated
            return Request(URL, callback=self.parse_lists)

    def parse_bookdetails(self, response):
            item = response.meta['item']
            if response.css('div.left a.bookPageGenreLink::text').getall()[0] is not None:
              item['genre1'] = response.css('div.left a.bookPageGenreLink::text').getall()[0]
            else:
              item['genre1'] = ''
            if response.css('div.left a.bookPageGenreLink::text').getall()[1] is not None:
              item['genre2'] = response.css('div.left a.bookPageGenreLink::text').getall()[1]
            else:
              item['genre2'] = ''
            if response.css('div.left a.bookPageGenreLink::text').getall()[2] is not None:
              item['genre3'] = response.css('div.left a.bookPageGenreLink::text').getall()[2]
            else:
              item['genre3'] = ''
            if response.css('div.left a.bookPageGenreLink::text').getall()[3] is not None:
              item['genre4'] = response.css('div.left a.bookPageGenreLink::text').getall()[3]
            else:
              item['genre4'] = ''
            return[item]

    def parse_lists(self, response):
        for bookslist in response.css('div.elementList div.left'):
            ratingscount = bookslist.xpath('.//*[@class="greyText smallText"]/text()').re(r'\s(\d{1,3}(?:,\d{3})*)\s')
            cleaned_ratingscount = [re.sub(r'\W', '', i) for i in ratingscount]
            rating = bookslist.xpath('.//*[@class="greyText smallText"]/text()').re(r'\d+\.\d+')
            converted_rating = [re.sub(r'\.', ',', i) for i in rating]
            booklink_raw = bookslist.css('a.bookTitle::attr(href)').get()
            if bookslist.css('a.bookTitle::text').get() is not None:
              booklink = 'https://goodreads.com' + booklink_raw
            item = goodreads_book_attributes_combined()
            title = bookslist.css('a.bookTitle::text').get()
            author = bookslist.xpath('.//*[@class="authorName"]/span/text()').extract_first()
            item['title'] = title
            item['author'] = author
            item['booklink'] = booklink
            item['ratingscount'] = cleaned_ratingscount
            item['rating'] = converted_rating

            yield Request(item['booklink'], meta={'item':item}, callback=self.parse_bookdetails)


        global count
        count = count - 1

        if (count > 0):

          next_page = response.css('a.next_page::attr(href)').extract_first()
          if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_lists)


