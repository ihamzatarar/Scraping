
import scrapy


class grepoolItem(scrapy.Item):

     model = scrapy.Field()
     brand = scrapy.Field()
     product = scrapy.Field()
     product_parent = scrapy.Field() 
     product_lang = scrapy.Field()
     file_urls  = scrapy.Field() 
     type = scrapy.Field()
     url  = scrapy.Field()
     thumb = scrapy.Field()
     source = scrapy.Field()


class ProductSpider(scrapy.Spider):
    name = 'product'
    allowed_domains = ['www.grepool.com']
    start_urls = ['https://www.grepool.com/en']

    def parse(self, response):
        for cat_sel in  response.xpath('//*[@class="header__nav-item "]/@href').extract():
            url = 'https://www.grepool.com' + cat_sel
            yield response.follow(url, callback=self.parse_listing)

    def parse_listing(self, response):
        for prod_url in response.xpath('//*[@class="products-list__image-wrapper u-veil"]/a/@href').getall():
            url = 'https://www.grepool.com' + prod_url
            yield response.follow(url, callback=self.parse_item)

    
    def parse_item(self, response):

        Type = response.css('div.download-file__item-header span::text').get().split()
        product_catag = response.css('.breadcrumbs__link::text').getall()

        items = grepoolItem()
        items['model']= response.css('.u-hide--s768 .p-small::text').get().split()[-1]
        items['brand'] = response.xpath('//html/head/meta[@name="application-name"]/@content').get().split()[-1]
        items['product'] = product_catag[1]
        items['product_parent'] = product_catag[0]
        items['product_lang'] = response.css('html').attrib['lang']
        items['file_urls'] = response.css('li:nth-child(1) .download-file__item').attrib['href']
        items['type'] = Type[0]+' '+ Type[1]
        items['url'] = response.xpath('//html/head/meta[@name="twitter:url"]/@content').get()
        items['thumb'] = response.css('.gallery__image').attrib['style'][22:-2]
        items['source'] = response.css('.header__logo').attrib['href']

        yield items

        
       
    