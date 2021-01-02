# -*- coding: utf-8 -*-
import re
import scrapy
import bs4

RE_MYSHOPIFY = re.compile(r"https?://[\w\d\-]+\.myshopify\.com/?")


class DiscoverySpider(scrapy.Spider):
    """Spider for scraping Shopify URLS from Google.

    Usage example:
    scrapy crawl GoogleSpider -a query="board games"

    If no query is provided, the spider does nothing.

    Warning:
    Tread lightly. Google does not like being scraped.
    """
    name = "DiscoverySpider"
    allowed_domains = ["google.com"]
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "ITEM_PIPELINES": {"shopify_spy.pipelines.DuplicateURLPipeline": 100}
    }

    def __init__(self, query=None, *args, **kwargs):
        """Constructs spider with start_urls determined by query.

        Keyword arguments:
        query -- search terms separated by spaces (default None)

        If no query is provided, start_urls is left empty.
        """
        super().__init__(*args, **kwargs)
        self.start_urls = [get_search_url(query)] if query else []
        self._rank_count = 1

    def parse(self, response):
        """Yields Shopify URLS and request for next page."""
        soup = bs4.BeautifulSoup(response.text, "lxml")
        elems = soup.find_all("a", href=RE_MYSHOPIFY)
        for elem in elems:
            url = RE_MYSHOPIFY.search(elem["href"])[0]
            rank = self._rank_count
            self._rank_count += 1
            yield {"url": url, "rank": rank}
        next_ = soup.find("a", attrs={"aria-label": "Next page", "href": True})
        if next_:
            yield scrapy.Request("https://www.google.com" + next_["href"])


def get_search_url(query, site="myshopify.com"):
    """Constructs Google search URL from query with site constraint."""
    terms = "+".join(query.split())
    return f"https://www.google.com/search?q={terms}+site:{site}"