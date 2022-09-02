
import scrapy
from scrapy import FormRequest, Request, Selector
import json


class LdSystemsSpider(scrapy.Spider):
    name = 'ld-systems.com'
    start_urls = ['https://www.ld-systems.com/en/support/']
    rfiles = set()
    rtypes = set()
    url = 'https://www.ld-systems.com/en/widgets/SupportAndDownloads'

    def parse(self, response):

        for category in response.css('.select-field option::attr(value)').getall():
            meta = dict()
            meta['category'] = category
            product = f'option[value="{category}"]::text'
            meta['product'] = response.css(product).get().strip('-').strip()
            headers = {
                'Accept': '*/*',
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }

            yield Request(
                url=self.url,
                callback=self.parse_article,
                method="POST",
                body=f"support_and_downloads%5Blast_selected_category%5D=&support_and_downloads%5Bcategory%5D={category}&__csrf_token=VqTng465j2IbIGgGV9dm09ffyGuJuU",
                headers=headers,
                meta=meta
            )

    def parse_article(self, response, **kwargs):

        for article in response.css('.select-field select[title="Product*"] option::attr(value)').getall():
            model = f'option[value="{article}"]::text'
            response.meta['model'] = response.css(model).get()
            category = response.meta.get('category')
            headers = {
                'Accept': '*/*',
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }

            yield Request(
                url=self.url,
                callback=self.parse_item,
                method="POST",
                body=f"support_and_downloads%5Blast_selected_category%5D={category}&support_and_downloads%5Bcategory%5D={category}&support_and_downloads%5Barticle%5D={article}&__csrf_token=VqTng465j2IbIGgGV9dm09ffyGuJuU",
                headers=headers,
                meta=response.meta
            )

    def parse_item(self, response, **kwargs):
        for pdf_sel in response.css('.table-link'):
            manual = dict()
            rtype = pdf_sel.css('::attr(title)').get()
            if rtype.lower() == 'user´s manual':
                rfile = pdf_sel.css("::attr(href)").get()
                if rfile in self.rfiles:
                    continue
                self.rfiles.add(rfile)
                self.rtypes.add(rtype)
                manual['file_urls'] = [rfile]
                manual['type'] = rtype
                manual['model'] = response.meta.get('model')
                manual['product'] = response.meta.get('product')
                manual['url'] = response.url
                manual['source'] = self.name
                manual['brand'] = "LD Systems"
                manual['product_lang'] = 'en'

                yield manual
