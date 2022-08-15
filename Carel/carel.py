import scrapy
from scrapy.spiders import SitemapSpider

class  CarelSpider(SitemapSpider):
    name = 'carel.com'
    sitemap_urls = ['https://www.carel.com/sitemap.xml']
    sitemap_rules = [('/product/','parse')]
    rfiles = set()


    def parse(self, response, **kwargs):
        manual = dict()
        for pdf_sel in response.css('.detail-documentation-title'):
            if pdf_sel.css('::text').get() == 'Manuals':
                try:
                    rfile = pdf_sel.xpath('//following-sibling::section').css('a::attr(href)').get().split("'")[1]
                    if rfile in self.rfiles:
                        continue
                    self.rfiles.add(rfile)
                    manual['file_urls'] = [rfile]
                except IndexError:
                    self.logger.info('File Not Found')
                    continue
                manual['type']= 'Manuals'
                manual['product'] = response.css('.breadcrumbs-nolink::text').get()
                manual['model']= response.css('.detail-title::text').get()
                manual['thumb'] = response.urljoin(response.css('.detail-image img::attr(src)').get())
                manual['url'] = response.url
                manual['source'] = self.name
                manual['brand'] = "Carel"
                manual['product_lang'] = response.css('html::attr(lang)').get().split('-')[0]

                yield manual
