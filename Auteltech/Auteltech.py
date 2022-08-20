import scrapy
import re
from manual_scraper_ext.items import Manual
class AuteltechSpider(scrapy.Spider):
    name = 'auteltech.com'
    start_urls = ['https://www.auteltech.com/mk3/3914.jhtml']
    rfiles = set()
    rtypes = set()



    def parse(self, response):
        for lang_sel in response.css('.laguage_div a::attr(href)').getall():
            yield response.follow(lang_sel, callback=self.parse_prod)

    def parse_prod(self, response):
        for cat_sel in response.css(".products_content"):
            meta = Manual()
            meta['product'] = cat_sel.css("h4::text").get()
            if 'https://' in cat_sel.css("a::attr(href)").get():
                url = cat_sel.css("a::attr(href)").get()
            else:
                url = response.urljoin(cat_sel.css("a::attr(href)").get())
            yield response.follow(url, callback=self.parse_listing, meta=meta)

    def parse_listing(self, response):
        for prod_url in response.css('.dt_content_item a::attr(href)').getall():
            url = response.urljoin(prod_url)
            yield response.follow(url, callback=self.parse_item, meta=response.meta)



    def parse_item(self, response, **kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            model = response.css('.pi_header_right h3::text').get()
            rtype = pdf_sel.xpath("preceding-sibling::div[1]/span/text()").get()
            types = [ 'User Manual', 'Quick Guide','Quick Start Guide','ユーザーマニュアル',
                            'クイックガイド','カタログ','同梱一覧','使用方法','ソフト登録方法','組立要領書',
                                    '取扱説明書','快速指引','说明书','_Sales_flyer','Packing List','FunctionList','Usermanual']

            try:
                for t in types:
                    if t  in rtype or t.lower() in rtype:
                        rtype = t

                model1 = model.split()
                for m in model1:
                    if m in rtype or m.lower() in rtype:
                        rtype = rtype.replace(m,'').strip()
                if '(' and ')' in rtype:
                    brackets = re.search(r'[(].*[)]',rtype).group(0)
                    rtype = rtype.replace(brackets,'')
            except:
                continue
            
            self.rtypes.add(rtype)
            manual['file_urls'] = [response.urljoin(rfile)]
            manual['type'] = rtype.strip('_')
            manual['model'] = model
            manual['product'] = response.meta.get('product')
            manual['thumb'] = response.urljoin(response.css('.pi_img img::attr(src)').get())
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Autel"
            manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

            yield manual
    
    def close(spider, reason):
        print(spider.rtypes)