# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
from openpyxl import Workbook
from openpyxl.styles import Font


class XlsxPipeline(object):

    def open_spider(self, spider):
        """Start scraping"""
        # Create an Excel workbook
        self._wb = Workbook()
        # Select the active spreadsheet
        self._ws = self._wb.active
        self._ws.title = spider.name
        self._ws.append(spider.item_data_label)
        row = list(self._ws.rows)[0]
        for cell in row:
            cell.font = Font(bold=True)

    def process_item(self, item, spider):
        # Append a row to the spreadsheet
        self._ws.append([item[label] for label in spider.item_data_label])
        return item

    def close_spider(self, spider):
        """Stop scraping"""
        # Save the Excel workbook
        self._wb.save(spider.output_filename + '.xlsx')