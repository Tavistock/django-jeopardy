# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from ../../models import Season, Episode, GameRound, Category, Question

class ScrapyJeopardyPipeline(object):
    def process_item(self, item, spider):
        if item['type'] == 'season':
            process_season(item)
        #elif item['type'] == 'episode':
        #    process_episode(item)
        #elif item['type'] == 'rounds':
        #    process_rounds(item)

def process_season(item):
    season = Season(start=get_date(item['start']),
                    end=get_date(item['end']),
                    title = item['title'])
    season.save()

def get_date(stamp):
    try:
        return time.strptime(stamp, '%Y-%m-%d')
    except Exception as e:
        return time.strptime(stamp, '%Y')
