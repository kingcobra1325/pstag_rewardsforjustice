from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from pstag_rewardsforjustice.spiders.rewardsforjustice import RewardsforjusticeSpider



configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(RewardsforjusticeSpider)
    reactor.stop()

crawl()
reactor.run()