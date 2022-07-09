from pstag_rewardsforjustice.lib.base_spider import BaseScrapySpider
from pstag_rewardsforjustice.items import PstagItem

from datetime import datetime

class RewardsforjusticeSpider(BaseScrapySpider):
    name = 'rewardsforjustice'
    allowed_domains = ['nextcloud.pst.ag']
    start_urls = [
                    'https://rewardsforjustice.net/wp-admin/admin-ajax.php',
                    ]

    item_data_label = [
                    'page_url',
                    'category',
                    'title',
                    'reward_amount',
                    'associated_organization',
                    'associated_location',
                    'about',
                    'image_url',
                    'date_of_birth',
                    ]
    
    post_payload = {
        "action":"jet_smart_filters",
        "provider":"jet-engine/rewards-grid",
        "query[_tax_query_crime-category][]":["1070","1071","1072","1073","1074"],
        "paged":"1",
        "settings[lisitng_id]":"22078",
        "settings[posts_num]":"50",
        "settings[max_posts_num]":"50",

    }

    # Set name for output files
    output_filename = f"{name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    custom_settings = { "FEEDS" : {
        f"{output_filename}.json":{
                                    "format": "json"
                                    },
        f"{output_filename}.xlsx":{
                                    "format": "xlsx"
                                    },
    }}

    def start_requests(self):
        self.meta_data.update({
            "payload":self.post_payload
            })
        return super().start_requests()

    def initial_parse(self, response):
        current_page = int(response.meta['payload']['paged'])
        self.logger.debug(f"Page |{current_page}|")
        response_json = response.json()
        parsesd_res = self.HtmlResponse(url="converting string...", body=response_json['content'], encoding='utf-8')

        raw_list = parsesd_res.xpath("//div[@data-elementor-type='jet-listing-items']/parent::div")
        self.logger.debug(f"RAW LIST COUNT: {len(raw_list)}")
        if raw_list:
            link_list = [x.xpath("./a/@href").get() for x in raw_list]
            category_list = [x.xpath(".//h2[text()='Kidnapping' or text()='Terrorism Financing' or text()='Acts of Terrorism' or text()='Terrorism - Individuals' or text()='Organizations']/text()").get() for x in raw_list]
            self.logger.debug(f"LINK LIST\n{link_list}")
            self.logger.debug(f"CAT LIST\n{category_list}")
            item_list = list(zip(link_list,category_list))
            self.logger.debug(f"ITEM LIST\n{item_list}")
            # Yield next list page
            current_page += 1
            new_meta = response.meta
            new_meta['payload']['paged'] = str(current_page)
            self.logger.debug(f"New Meta - |{new_meta}|")
            yield self.FormRequest(
                    url=response.url,
                    formdata=new_meta['payload'],
                    callback=self.initial_parse, 
                    errback=self.errback_httpbin,
                    meta=new_meta,
                    dont_filter=True
                    )
            for link,category in item_list:
                item_meta = response.meta
                item_meta['category'] = category
                yield self.ScrapyRequest(
                    url=link,
                    callback=self.item_parse,
                    errback=self.errback_httpbin,
                    meta=item_meta,
                    dont_filter=True
                    )

    def item_parse(self,response):
        metadata = response.meta
        result = self.copy_empty_results(metadata['item_data_label'])
        self.logger.debug(f"Result Empty Dict: {result}")
        result['page_url'] = response.url
        result['category'] = metadata['category']
        result['title'] = response.xpath("//h2[@class='elementor-heading-title elementor-size-default']/text()").get()
        result['about'] = "\n".join(response.xpath("//div[@data-widget_type='theme-post-content.default']/div/p/text()").getall())
        result['reward_amount'] = response.xpath("//h4[contains(text(),'Reward')]/parent::div/parent::div/following-sibling::div/div/h2/text()").get()
        result['associated_organization'] = '\n'.join(response.xpath("//p[contains(text(),'Associated Organization')]/a/text()").getall())
        result['associated_location'] = response.xpath("//h2[contains(text(),'Associated Location')]/parent::div/parent::div/following-sibling::div//span/text()").get()
        result['image_url'] = '\n'.join(response.xpath("//div[contains(@class,'terrorist-gallery')]//img/@src").getall())
        raw_dob = response.xpath("//h2[contains(text(),'Date of Birth')]/parent::div/parent::div/following-sibling::div/div/text()").get()
        if raw_dob:
            raw_dob = raw_dob.replace("\t","")
            self.logger.debug(f"Raw Date of Birth: |{raw_dob}|")
            cleaned_dob = self.perform_dob_regex(raw_dob)
            self.logger.debug(f"Cleaned Date of Birth: |{cleaned_dob}|")
            parsed_date = " - ".join([self.datetime.strptime(x,"%B %d, %Y").isoformat() for x in cleaned_dob])
            result['date_of_birth'] = parsed_date
        
        self.logger.debug(result)
        yield self.load_item_from_dict(result,PstagItem)