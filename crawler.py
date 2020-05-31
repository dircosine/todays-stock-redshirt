import requests
from bs4 import BeautifulSoup

base_url = "https://finance.naver.com/item/main.nhn?code="


def crawl(code):
    row_dict = {'name': 'N/A', 'code': 'N/A', 'market': 'N/A'}
    price = {
        'today': 'N/A',
        'exday': 'N/A',
        'change': 'N/A',
        'changePercent': 'N/A',
        'high': 'N/A',
        'low': 'N/A',
        'start': 'N/A',
        'volume': 'N/A',
        'tradingValue': 'N/A',
    }
    more = {
        'cap': 'N/A',
        'capRank': 'N/A',
        'amountOfListed': 'N/A',
        'week52high': 'N/A',
        'week52low': 'N/A',
        'per': 'N/A',
        'pbr': 'N/A',
        'dividendYield': 'N/A',
        'industryPer': 'N/A',
        'industryChange': 'N/A'
    }

    target_url = base_url + code
    webpage = requests.get(target_url)
    soup = BeautifulSoup(webpage.content, "html.parser")

    invest_info = soup.find(attrs={'tab_con1'})
    td_elements = invest_info.find_all('td')

    name = soup.find(attrs={'wrap_company'}).find('h2').string
    row_dict['name'] = name

    code
    row_dict['code'] = code

    market = soup.find(attrs={'description'}).find('img')['alt']
    row_dict['market'] = market

    if (market != '코스피' and market != '코스닥'):
        raise TypeError

    # *** price
    price['today'] = soup.find(attrs={"no_today"}).find(attrs={"blind"}).string

    no_exday = soup.find(attrs={"no_exday"}).find_all(attrs={"blind"})
    price_change = no_exday[0].string
    price_change_percent = no_exday[1].string
    if soup.find(attrs={"no_exday"}).find(attrs={'minus'}):
        price['change'] = "-" + price_change
        price['changePercent'] = "-" + price_change_percent
    else:
        price['change'] = "+" + price_change
        price['changePercent'] = "+"+price_change_percent

    no_info = soup.find(attrs={"no_info"}).find_all(attrs={'blind'})
    price['exday'] = no_info[0].string
    price['high'] = no_info[1].string
    price['volume'] = no_info[3].string
    price['start'] = no_info[4].string
    price['low'] = no_info[5].string
    price['tradingValue'] = no_info[6].string

    if price['volume'] == '0':
        raise ValueError

    row_dict['price'] = price

    # *** more
    cap = td_elements[0].find('em').string
    cap = cap.replace('\t', '').replace('\n', '').replace('조', '')
    more['cap'] = cap

    cap_rank = td_elements[1].find('em').string
    more['capRank'] = cap_rank

    amount_of_listed = td_elements[2].find('em').string
    more['amountOfListed'] = amount_of_listed

    week_52_high = td_elements[8].find_all('em')[0].string
    more['week52high'] = week_52_high

    week_52_low = td_elements[8].find_all('em')[1].string
    more['week52low'] = week_52_low

    per = td_elements[9].find_all('em')[0].string
    more['per'] = per

    pbr = td_elements[11].find_all('em')[0].string
    more['pbr'] = pbr

    dividend_yield = td_elements[12].find_all('em')[0].string
    more['dividendYield'] = dividend_yield

    industry_per = td_elements[13].find_all('em')[0].string
    more['industryPer'] = industry_per

    industry_change = td_elements[14].find_all('em')[0].string
    industry_change = industry_change.replace(
        '\n', '').replace('\t', '').replace('%', '')
    more['industryChange'] = industry_change

    row_dict['more'] = more

    return row_dict
