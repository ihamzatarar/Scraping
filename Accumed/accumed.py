

from manual_scraper_ext.items import Manual


class AccumedComBrSpider(scrapy.Spider):
    name = 'accumed.com.br'
    start_urls = ['https://www.accumed.com.br/downloads/']
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        for cat_sel in response.css('.vp-filter__item a'):
            meta = dict()
            meta['product'] = cat_sel.css("::text").get().strip()
            url = 'https://www.accumed.com.br' + cat_sel.css("::attr(href)").get()
            if url != 'https://www.accumed.com.br/downloads/':
                yield response.follow(url, callback=self.parse_item, meta=meta)

    def parse_item(self, response, **kwargs):
        for pdf_sel in response.css('.vp-portfolio__item-meta'):
            manual = Manual()
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles or '.pdf' not in rfile:
                continue
            self.rfiles.add(rfile)
            manual['file_urls'] = [rfile]
            manual['type'] = 'manuais'
            product = response.meta.get('product')
            manual['product'] = product
            try:
                excluded_words = ['leite','tens','pressão']
                title = pdf_sel.css('h2::text').get().strip().replace('G-Tech', '')
                model = ''
                if '-' in title:
                    for i in title.split('-')[1].split():
                        if i.lower() in excluded_words:
                           continue
                        else:
                             model += i + ' '
                else:
                    for i in title.split():
                        if product[:2] in i or i.lower() in excluded_words:
                            continue
                        if i[0].isupper() or i.isnumeric():
                            model += i + ' '
                if not model:
                    manual['model'] = title
                manual['model'] = model.strip().capitalize()
            except (AttributeError, IndexError):
                continue

            if not manual['model']:
                continue
            manual['model'] = manual['model'].replace("!", "").strip()
            manual['thumb'] = pdf_sel.xpath('./../../preceding-sibling::div[1]').css('img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "G-Tech"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            self.rtypes.add(manual['type'])
            yield manual

    def close(spider, reason):
        print(spider.rtypes)