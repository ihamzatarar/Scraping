from manual_scraper_ext.items import Manual

from scrapy.spiders import SitemapSpider


class GenieSpider(SitemapSpider):
    name = 'genie-online.de'
    sitemap_urls = ['https://www.genie-online.de/sitemap.xml']
    sitemap_rules = [('/product/', 'parse')]
    rfiles = set()
    rtypes = set()

    def parse(self, response):
        support_sel = response.css(
            '#lawmj6cx4udxy6w2xgzab6ml3qp0t59v a::attr(href)').get()
        yield response.follow(support_sel, callback=self.parse_item)

    def parse_item(self, response, **kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get()
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.xpath('./../preceding-sibling::th[1]/text()').get()
            if not rtype:
                continue
            self.rtypes.add(rtype)
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css(
                'h1::text').get().strip('GENIE').strip()
            manual['product'] = response.css('.breadcrumb a::text').getall()[2]
            manual['product_parent'] = response.css(
                '.breadcrumb a::text').getall()[1]
            manual['thumb'] = response.css(
                'div.item.active img::attr(src)').get()
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = "Genie"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def close(spider, reason):
        print(spider.rtypes)
