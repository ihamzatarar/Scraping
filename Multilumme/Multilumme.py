import scrapy




class MultilummeSpider(scrapy.Spider):
    name = 'Multilumm.com'
    start_urls = ['http://multilumme.com/']
    rfiles = set()

    def parse(self, response): 
        for cat_sel in response.css('li a::attr("href")').getall():
            if cat_sel.startswith('/shop/'):
                url = response.urljoin(cat_sel)
                yield response.follow(url, callback=self.parse_listing)
        
    def parse_listing(self, response):
        for product in response.css('h3 a::attr(href)').getall():
            prod_url = response.urljoin(product)
            yield response.follow(prod_url, callback=self.parse_item)

        
    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
           rfile = pdf_sel.css("::attr(href)").get()
           if rfile in self.rfiles:
            continue
           self.rfiles.add(rfile)
           manual['file_urls'] = rfile
           try:
            manual['type'] = response.css('a[href*=".pdf"]::text').get().split()[1].capitalize()
           except IndexError:
            return
           try:
            manual['model'] = response.css(".good-title::text").get().split()[-1].upper()
           except IndexError:
                self.logger.info("Model not found")
                return

           manual['product'] = response.css('[name="H2"]::attr(content)').get().removesuffix('s') 
           manual['thumb'] = response.urljoin(response.css("[class='gphoto big']::attr(src)").get())
           manual['url'] = response.url
           manual['source'] = self.name
           manual['brand'] = "LUMME"
           manual['product_lang'] = 'en'
           
           yield manual
