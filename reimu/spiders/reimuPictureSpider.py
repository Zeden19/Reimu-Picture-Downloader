from pathlib import Path
import scrapy
from scrapy import Selector


def parse_item(response):
    EXCLUDED_TAGS = {"ass", "comic", "doujin", "bondage", "tied_up", "panties", "underwear", "pantyshot", "death"}
    tags = response.css("ul li.tag a *::text").getall()
    if EXCLUDED_TAGS.isdisjoint(tags):
        image_urls = [response.xpath('//*[(@id = "image")]').attrib['src']]
        yield {
            'image_urls': image_urls
        }


class PageSpider(scrapy.Spider):
    name = "reimu"
    start_urls = [
        'https://safebooru.org/index.php?page=post&s=list&tags=hakurei_reimu+-rating%3asafe=0',
    ]
    def parse(self, response):
        for preview in response.css('div span.thumb a'):
            imageLink = "https://safebooru.org/" + preview.attrib["href"]
            yield scrapy.Request(url=imageLink, callback=parse_item)

        nextPage = [s for s in response.css('div.pagination a').getall() if ("next" in s)]
        if len(nextPage) == 0:
            nextPage = None
        nextPage = Selector(text=nextPage[0]).css("a::attr(href)").get()

        if nextPage is not None:
            nextPage = response.urljoin(nextPage)
            yield scrapy.Request(nextPage, callback=self.parse)
