
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor



class BaumaticItem(scrapy.Item):

     model = scrapy.Field()
     brand = scrapy.Field()
     product = scrapy.Field() 
     product_lang = scrapy.Field()
     file_urls  = scrapy.Field()
     File_type = scrapy.Field()
     url  = scrapy.Field()
     thumb = scrapy.Field()
     source = scrapy.Field()



class ProductSpider(CrawlSpider):
    name = 'product'
    start_urls = ['http://Baumatic.com.au/']

    temp = ''  

    #Getting Data of all types of Dishwashers using rules
    rules = (
        Rule(LinkExtractor(allow ='products/dishwashers',deny=['freestanding-dishwasher','semi-integrated-dishwashers','fully-integrated-dishwashers'])),
        Rule(LinkExtractor(allow ='freestanding-dishwasher'),callback='linkgetter'),
        Rule(LinkExtractor(allow ='semi-integrated-dishwashers'), callback='linkgetter'),
        Rule(LinkExtractor(allow ='fully-integrated-dishwashers'), callback='linkgetter'),      #Couldn't get to exact links of products using Rules
    )


    def linkgetter(self,response):
        Links = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "product-name", " " ))]//a/@href').extract()
        complete_urls = ([ 'https://www.Baumatic.com.au' + link for link in Links ]) #List of urls of products           


        for i in complete_urls:
            ProductSpider.temp = i  #Saving url of current product
            yield response.follow(i,callback=self.parse_item)


        
        
       



    def parse_item(self, response):

        items = BaumaticItem()
        title = response.css('.h3::text').get().split()
        items['model'] = title[-1]
        items['brand'] = 'Baumatic'
        items['product'] = 'Dishwasher'
        items['product_lang'] = 'eng'
        items['file_urls'] = response.css('.mar5:nth-child(3) .button ').attrib['href']
        items['File_type'] = response.css('.mar5:nth-child(3) .button::text ').get()
        items['thumb'] = response.css('.product-image img').attrib['src']
        items['url'] = ProductSpider.temp
        items['source'] = ProductSpider.start_urls[0]
        yield  items
       
       
       





