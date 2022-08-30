from manual_scraper_ext.items import Manual

from scrapy.spiders import SitemapSpider


class NativeInstrumentsSpider(SitemapSpider):
    name = 'native-instruments.com'
    sitemap_urls = [
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_en.xml'
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_de.xml',
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_fr.xml',
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_zh.xml',
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_jp.xm',
        'https://www.native-instruments.com/fileadmin/ni_media/sitemaps/sitemap_es.xml']
    sitemap_rules = [('/downloads/', 'parse')]
    rfiles = set()
    rtypes = set()
    thumb = ''

    def parse(self, response, **kwargs):
        manual = dict()

        for pdf_sel in response.css('a[href*=".pdf"]'):
            rfile = pdf_sel.css("::attr(href)").get().lstrip('//')
            if rfile in self.rfiles:
                continue
            self.rfiles.add(rfile)
            rtype = pdf_sel.css('::attr(title)').get().replace('DOWNLOAD ', '')
            if not rtype:
                continue
            self.rtypes.add(rtype)
            if 'drivers-other-files/' in response.url:
                continue
            manual['file_urls'] = [rfile]
            manual['type'] = rtype
            manual['model'] = response.css('h1 a::text').get()
            manual['product'] = response.css(
                'title::text').get().split(':')[0].strip()
            try:
                thumb_url = response.urljoin(
                    response.css('h1 a::attr(href)').get())
                yield response.follow(thumb_url, callback=self.parse_thumb)
            except:
                continue
            manual['thumb'] = self.thumb
            manual['url'] = response.url
            manual['source'] = self.name
            manual['brand'] = " Native Instruments"
            manual['product_lang'] = response.css(
                'html::attr(lang)').get().split('-')[0]

            yield manual

    def parse_thumb(self, response):
        self.thumb = response.urljoin(response.css(
            '.image-container img::attr(data-src)').get()).replace('[[display]]', 't@2x')

    def close(spider, reason):
        print(spider.rtypes)
