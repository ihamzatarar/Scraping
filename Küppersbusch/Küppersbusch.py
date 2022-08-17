import scrapy

class HomekueppersbuschSpider(scrapy.Spider):
    name = 'home-kueppersbusch.com'
    start_urls = ['https://www.home-kueppersbusch.com/global/']
    rfiles = set()


    def parse(self, response):
        for lang_sel in response.css('link[rel="alternate"]::attr(href)').getall()[:36]:
            yield response.follow(lang_sel, callback=self.parse_categ)

    def parse_categ(self, response):
        listing_No = 0
        for categ in response.css('.sub-menu a'):
            meta = dict()
            meta['product_parent'] = categ.css('::text').get()
            url = response.urljoin(categ.css('::attr(href)').get())
            yield response.follow(url, callback=self.parse_sub_categ,meta= meta)
            listing_No += 1
            if listing_No == 6:
                return
    
    def parse_sub_categ(self, response):
        for sub_categ in response.css('#categories_menu a'):
            response.meta['product'] = sub_categ.css('::text').get()
            url = sub_categ.css('::attr(href)').get()
            yield response.follow(url, callback=self.parse_product,meta=response.meta)
    

    def parse_product(self, response):
        for prod_url in response.css('.teka-button::attr(href)').getall():
            yield response.follow(prod_url, callback=self.parse_item,meta=response.meta)



    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = rfile
            manual['type'] = pdf_sel.css('strong::text').get()
            manual['product'] = response.meta.get('product')
            manual['product_parent'] = response.meta.get('product_parent')
            manual['model'] = response.css('.ref::text').get()
            manual['thumb'] = response.css('#main-image-single::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Küppersbusch"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            yield manual