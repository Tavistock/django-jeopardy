import scrapy
import re

class JeopardySpider(scrapy.Spider):
    name = 'jeopardy'
    allowed_domains = ["j-archive.com"]
    start_urls = ['http://www.j-archive.com/listseasons.php']

    def parse(self, response):
        return self.parse_seasons(response)

    def parse_seasons(self, response):
        for sel in response.xpath('//*[@id="content"]/table/tr'):
            link = sel.xpath('td/a/@href').extract()[0]
            name = ''
            if sel.xpath('td/a/text()').extract() != []:
                name = sel.xpath('td/a/text()').extract()[0]
            else:
                name = sel.xpath('td/a/i/text()').extract()[0]
            dates = sel.xpath('td[2]/text()').re('[\d-]+')

            yield {
                    'name': name,
                    'start': dates[0],
                    'end': dates[1]
                    }

            request = scrapy.Request(response.urljoin(link),
                                     callback=self.parse_season)
            request.meta['season'] = name
            yield request

    def parse_season(self, response):
        for sel in response.xpath('//*[@id="content"]/table/tr'):
            name_date = sel.xpath('td[1]/a/text()')

            link = sel.xpath('td[1]/a/@href').extract()[0]
            name = name_date.re('.*#\d+')[0]
            date_aired = name_date.re(',.*?([\d-]+)')[0]
            title = sel.xpath('td[2]/text()').extract()[0].strip()
            subtitle = sel.xpath('td[3]/text()').extract()[0].strip()
            game_id_string = re.compile('game_id=(\d*)').search(link).groups()[0]
            game_id = int(game_id_string)
            yield {
                    'name': name,
                    'game_id': game_id,
                    'title': title,
                    'subtitle': subtitle,
                    'date_aired': date_aired,
                    'season': response.meta['season']
                    }

            request = scrapy.Request(link,
                                     callback=self.parse_game)
            request.meta['game_id'] = game_id
            yield request

    def debug_season(self, response):
        """helper method because you can hand a meta in at the command line"""
        response.meta['season'] = 'debug'
        return self.parse_season(response)

    def parse_game(self, response):
        selector = response.xpath('//div[@id="content"]/div')[3:]
        for num, sel in enumerate(selector):
            round_number = num
            round_type = sel.xpath('@id').extract()[0]
            game_id = response.meta['game_id']
            yield {
                    'round_number': round_number,
                    'round_type': round_type,
                    'episode': game_id
                    }

            if round_type == 'final_round':
                #self.parse_final_round(sel, (game_id, round_number))
                yield {"pass": True}
            else:
                self.parse_round(sel, (game_id, round_number))


    def debug_game(self, response):
        response.meta['game_id'] = 'debug'
        return self.parse_game(response)

    def parse_final_round(self, selector, uniq_id):
        pass

    def parse_round(self, selector, game_id):
        category = sel.xpath('table/tr/td[@class="category"]')
        category_name = category.xpath('/table/tr/td[@class="category_name"]')
        length = len(category_name)
        for row, name in enumerate(category_name):
            yield {
                    'type': 'category',
                    'name': name,
                    'game_round': uniq_id
                }
            self.parse_question(sel, row, length, uniq_id + (name,))

    def parse_question(self, sel, offset, total, uniq_id):
        questions = sel.xpath('table/tr/td[@class="clue"]')
        for row in range(0, 5):
            q = questions[(row*total)+offset]
            answer = q.re('correct_response&quot;&gt;(.+?)&lt;')[0]
            question = (q.xpath('table/tr/td[@class="clue_text"]/text()')
                    .extract()[0])
            value = (q.xpath('table/tr/td/div/table/tr/td[@class="clue_value"]/text()')
                    .extract()[0])

            yield {
                    'value': value,
                    'question': question,
                    'answer': answer,
                    'category': uniq_id
                    }

