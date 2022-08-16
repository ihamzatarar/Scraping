import scrapy

class  CarelSpider(scrapy.Spider):
    name = 'carel.com'
    start_urls = ['https://www.carel.com/']
    rfiles = set()

    def parse(self, response):
        for lang_sel in response.css('#selectCountry a::attr(href)').getall():
            yield response.follow(lang_sel, callback=self.parse_parent)

    def parse_parent(self, response):
        listing = 0
        for catag in response.css('.nav-third.element-to-hide'):
            meta = dict()
            meta['level_1'] = catag.xpath('preceding-sibling::a[1]/text()').get().strip()
            for sub_catag in catag.css('a'):
                meta['level_2'] = sub_catag.css('::text').get()
                url = sub_catag.css('::attr(href)').get()
                yield response.follow(url, callback=self.parse_product,meta=meta)
            listing += 1
            if listing == 17:
                return

    def parse_product(self, response):
        for prod_url in response.css('.contents.level-3 a::attr(href)').getall():
            url = response.urljoin(prod_url)
            yield response.follow(url, callback=self.parse_item,meta=response.meta)

    def parse_item(self, response, **kwargs):
        manual = dict()
        typeList = ['用户手册','Manuals','Manuály','Manuali','Instrukcje obsługi','Инструкции по применению','*Посібники']
        for pdf_sel in response.css('.detail-documentation-title'):
            if pdf_sel.css('::text').get() in typeList:
                for pdf in pdf_sel.xpath('following-sibling::section').css('a::attr(href)').getall():
                    try:
                        rfile = pdf.split("'")[1]
                    except IndexError:
                        continue
                    if rfile in self.rfiles:
                        continue
                    self.rfiles.add(rfile)
                    manual['file_urls'] = [rfile]
                    manual['type']= pdf_sel.css('::text').get()
                    manual['product'] = response.meta.get('level_2').replace('NA','')
                    manual['model']= response.css('.detail-title::text').get()
                    manual['thumb'] = response.urljoin(response.css('.detail-image img::attr(src)').get())
                    manual['url'] = response.url
                    manual['source'] = self.name
                    manual['brand'] = "Carel"
                    manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

                    yield manual
