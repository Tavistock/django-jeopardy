import re
import scrapy


class JeopardySpider(scrapy.Spider):
    name = 'jeopardy'
    allowed_domains = ["j-archive.com"]
    start_urls = ['http://www.j-archive.com/listseasons.php']
    limit = None
    start = 0

    def __init__(self, limit=None, start=None, *args, **kwargs):
        super(JeopardySpider, self).__init__(*args, **kwargs)
        if limit:
            self.limit = int(limit)
        if start:
            self.start = int(start)

    def parse(self, response):
        return self.parse_seasons(response)

    def parse_seasons(self, response):
        seasons = response.xpath('//*[@id="content"]/table/tr')
        to_crawl = seasons[self.start:]
        if self.limit:
            to_crawl = seasons[:self.limit]

        for sel in to_crawl:
            link = sel.xpath('td/a/@href').extract()[0]
            title = ''
            if sel.xpath('td/a/text()').extract() != []:
                title = sel.xpath('td/a/text()').extract()[0]
            else:
                title = sel.xpath('td/a/i/text()').extract()[0]
            dates = sel.xpath('td[2]/text()').re('[\d-]+')

            yield {
                'type': 'season',
                'title': title,
                'start': dates[0],
                'end': dates[1]
            }

            request = scrapy.Request(response.urljoin(link),
                                     callback=self.parse_season)
            request.meta['season'] = title
            yield request

    def parse_season(self, response):
        for sel in response.xpath('//*[@id="content"]/table/tr'):
            name_date = sel.xpath('td[1]/a/text()')

            link = sel.xpath('td[1]/a/@href').extract()[0]
            name = name_date.re('.*#\d+')[0]
            date_aired = name_date.re(',.*?([\d-]+)')[0]
            title = sel.xpath('td[2]/text()').extract()[0].strip()
            subtitle = sel.xpath('td[3]/text()').extract()[0].strip()
            game_id_string = (re
                              .compile('game_id=(\d*)')
                              .search(link)
                              .groups()[0])
            game_id = int(game_id_string)
            yield {
                'type': 'epidsode',
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
        selectors = response.xpath('//div[@id="content"]/div')[3:]
        game_id = None
        rounds = []
        for num, sel in enumerate(selectors):
            round_number = num
            round_type = sel.xpath('@id').extract()[0]
            game_id = response.meta['game_id']

            categories = None
            if round_type == 'final_jeopardy_round':
                categories = self.read_final_round(sel)
            else:
                categories = self.read_round(sel)

            rounds.append({
                'round_number': round_number,
                'round_type': round_type,
                'categories': categories
                })

        yield {
            'type': 'rounds',
            'episode': game_id,
            'rounds': rounds
        }

    def debug_game(self, response):
        response.meta['game_id'] = 'debug'
        return self.parse_game(response)

    def read_final_round(self, selector):
        name = (selector
                .xpath('table/tr/td[@class="category"]')
                .xpath('div/table/tr/td[@class="category_name"]/text()')
                .extract()[0])
        question = ''.join(
            (selector
                .xpath('table/tr/td[@class="clue"]')
                .xpath('table/tr/td[@class="clue_text"]/node()')
                .extract()))
        answer = selector.re('correct_response.*&quot;&gt;(.+?)&lt;/em&gt;')[0]

        return [{
            'type': 'category',
            'name': name,
            'questions': [{
                'type': 'question',
                'daily_double': False,
                'value': 0,
                'question': question,
                'answer': answer
            }]
        }]

    def read_round(self, selector):
        category = selector.xpath('table/tr/td[@class="category"]')
        category_names = (category
                          .xpath('table/tr/td[@class="category_name"]/text()')
                          .extract())
        length = len(category_names)
        catagories = []
        for row, name in enumerate(category_names):
            questions = self.read_questions(selector, row, length)
            catagories.append({
                'type': 'category',
                'name': name,
                'questions': questions
                })

        return catagories

    def read_questions(self, selector, offset, total):
        questions_sel = selector.xpath('table/tr/td[@class="clue"]')
        questions = []
        for row in range(0, 5):
            q = questions_sel[(row * total) + offset]
            length = len(q.xpath('node()').extract())
            if (length > 1):
                answer = (
                    q
                    .re('correct_response.*?&quot;&gt;(.+?)&lt;/em&gt;')[0])
                question = ''.join(
                    (q.xpath('table/tr/td[@class="clue_text"]/node()')
                        .extract()))
                value_sel = (q
                             .xpath('table/tr/td/div/table/tr')
                             .css('.clue_value, .clue_value_daily_double')
                             .xpath('text()'))
                value = int(value_sel.re('[\d,]+')[0].replace(',', ''))

                daily_double = False
                if len(value_sel.re('DD')) > 0:
                    daily_double = True
                else:
                    daily_double = False

                questions.append({
                    'type': 'question',
                    'daily_double': daily_double,
                    'value': value,
                    'question': question,
                    'answer': answer
                })
        return questions
