import scrapy

class  AccumedSpider(scrapy.Spider):
    name = ' accumed.com'
    start_urls = ['https://www.accumed.com.br/downloads/']
    rfiles = set()

    def parse(self, response):
        for cat_sel in response.css('.vp-filter__item a'):
            meta = dict()
            meta['product'] = cat_sel.css("::text").get().strip()
            url = 'https://www.accumed.com.br' + cat_sel.css("::attr(href)").get()
            if url != 'https://www.accumed.com.br/downloads/':
                yield response.follow(url, callback=self.parse_item, meta=meta)
    

    def parse_item(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('.vp-portfolio__item-meta'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = [rfile]
            manual['type']= 'manuais'
            product = response.meta.get('product')
            manual['product'] = product
            try:
                title = pdf_sel.css('h2::text').get().strip().replace('G-Tech','')
                model = ''
                if '-' in title:
                    model = title.split('-')[1]
                else:
                    for i in title.split():
                        if product[:2] in i:
                            continue
                        if i[0].isupper() or i.isnumeric():
                            model += i + ' ' 
                manual['model']= model
            except (AttributeError,IndexError):
                continue
            
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "G-Tech"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            yield manual
