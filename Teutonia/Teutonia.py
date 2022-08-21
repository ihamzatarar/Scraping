import scrapy
from manual_scraper_ext.items import Manual
class TeutoniaSpider(scrapy.Spider):
    name = 'teutonia.com'
    start_urls = ['https://en.teutonia.com/category/Barnvagnar']
    rfiles = set()
    rtypes = set()


    def parse(self, response):
        for prod_url in response.css('.product-box  '):
            meta = dict()
            meta['model_2'] = prod_url.css('.code::text').get()
            meta['product'] = response.css('h1::text').get()
            url = response.urljoin(prod_url.css("a::attr(href)").get())
            yield response.follow(url, callback=self.parse_item, meta=meta)


    def parse_item(self, response, **kwargs):
        manual = Manual()


        pdfs = response.css(".file-download-list span::text").getall()
        pdf = [pp for pp in pdfs if 'Manual' in pp or 'manual' in pp]
        if not pdf:
            self.logger.warning("No manual found")
            return

        for pdf_sel in response.css('.file-download-list'):
            rfile = pdf_sel.css("a::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            model = response.css('h1 strong::text').get()
            rtype = pdf_sel.css("span::text").get().replace(model,'').strip()
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype
            manual['model'] = model
            manual['model_2'] = response.meta.get('model_2')
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.css('#image-1 a::attr(href)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Teutonia"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            yield manual
    
    def close(spider, reason):
        print(spider.rtypes)