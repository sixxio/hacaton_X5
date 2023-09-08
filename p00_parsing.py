from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver import Keys, ActionChains
import bs4, time, random, pandas as pd


'''
First part: parsing list of shops to get primary list contain shop_id, rating, rates_number and address.
'''

driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://yandex.ru/maps/2/saint-petersburg/?ll=30.315635%2C59.938951&z=10')
inp = driver.find_element(By.CLASS_NAME, 'input__control')
inp.click()
inp.send_keys('пятерочка')
inp.send_keys(Keys.RETURN)
driver.implicitly_wait(100)

scroll_zone = driver.find_element(By.CLASS_NAME, "search-list-view")
scroll_zone.click()

zoom = driver.find_element(By.CSS_SELECTOR, 'body > div.body > div.app > nav > div.map-controls-view > div > div.map-controls-view__main-controls > div:nth-child(1) > div > div > div > div.zoom-control__zoom-out > button')
zoom.click()
zoom.click()

scroll_zone.click()

for i in range(250):
    print(f'Progress: {(i+1)/2.5 :3}%.')
    ActionChains(driver)\
    .key_down(Keys.PAGE_DOWN)\
    .key_up(Keys.PAGE_DOWN)\
    .perform()
    time.sleep(random.randint(1,5)/10)

page = driver.execute_script("return document.documentElement.outerHTML")
print(f'Total: {len(bs4.BeautifulSoup(page).find_all(name = 'li'))} shops.')


shops = []
shop = {}
j=0
elems = bs4.BeautifulSoup(page).find_all(class_ = 'search-business-snippet-view')
for i in elems:
    try:
        shops += [{ 'link' : 'https://yandex.ru' + i.find(class_='search-business-snippet-view__rating').get('href'),
                    'id' : i.find(class_='search-business-snippet-view__rating').get('href').split('/')[-3],
                    'address' : i.find(class_='search-business-snippet-view__address').text,
                    'rating' : float(i.find(class_='search-business-snippet-view__rating').text.replace(u'Рейтинг\xa0','').replace(',','.').split(' ')[0][:3]),
                    'rates' : int(i.find(class_='search-business-snippet-view__rating').text.replace(u'Рейтинг\xa0','').replace(',','.').split(' ')[0][3:])}]
        j+=1
        print(j)
    except:
        pass

'''
Saving shops list to csv/xlsx/parquet with gzip compression.
'''

shops_df = pd.DataFrame(shops)
shops_df.to_csv('shops_rates.csv', index=False)
shops_df.to_excel('shops_rates.xlsx', index=False)
shops_df.to_parquet('shops_rates.parquet.gz', index=False, compression='gzip')



'''
Second part: for each shop from previuos list we go to reviews page and extract most part of reviews and rates by artefacts such as fruits, vegetables, availability, etc.
'''

all_shops_reviews = pd.DataFrame()
all_topics = []
driver = webdriver.Chrome()
driver.maximize_window()
j=1
for id in ids:
    try:
        print(j)
        j+=1
        driver.get(f'https://yandex.ru/maps/org/pyatyorochka/{id}/reviews/')

        footer = driver.find_element(By.CLASS_NAME, "business-reviews-card-view")
        footer.click()

        for i in range(100):
            ActionChains(driver)\
            .key_down(Keys.PAGE_DOWN)\
            .key_up(Keys.PAGE_DOWN)\
            .perform()
            time.sleep(random.randint(1,30)/100)

        page = driver.execute_script("return document.documentElement.outerHTML")
        soup = bs4.BeautifulSoup(page)
        topics = {'id' : id, 
                    'total_reviews': int(soup.find(class_ = 'card-section-header__title _wide').text.split(' ')[0]),
                    'total_rates': int(soup.find(class_ = 'business-rating-amount-view _summary').text.split(' ')[0])}
        for i in soup.find_all(class_ = 'carousel__item _align_center'):
            if i.find(class_ = 'business-aspect-view__text') != None:
                topics.update({i.find(class_ = 'business-aspect-view__text').text.split(' • ')[0] + '_pct' : int(i.find(class_ = 'business-aspect-view__text').text.split(' • ')[1].replace('%','')),
                i.find(class_ = 'business-aspect-view__text').text.split(' • ')[0] : int(i.find(class_ = 'business-aspect-view__count').text.split(' ')[0])})
        all_topics += [topics]

        reviews = []
        for i in soup.find_all(class_ = 'business-reviews-card-view__review'):
            reviews += [{'rate' : len(i.find_all(class_ = 'inline-image _loaded business-rating-badge-view__star _full _size_m')),
                        'text' : i.find(class_ = 'business-review-view__body-text').text,
                        'date' : i.find(class_ = 'business-review-view__date').meta.get('content')}]
        one_shop_reviews = pd.DataFrame(reviews)
        one_shop_reviews['id'] = id
        all_shops_reviews = pd.concat([all_shops_reviews, one_shop_reviews])
    except:
        pass


'''
Saving all reviews and full shops rates to csv/xlsx/parquet with gzip compression.
'''

topics_df = pd.DataFrame(all_topics)
['id'] = pd.to_numeric(topics_df['id'])

joined = shops_df.join(topics_df, how='inner', rsuffix='_1').drop(columns='id_1')
joined.to_csv('shops_rates_and_topics.csv', index=False)
joined.to_excel('shops_rates_and_topics.xlsx', index=False)
joined.to_parquet('shops_rates_and_topics.parquet.gz', index=False, compression='gzip')

all_shops_reviews.to_csv('shops_reviews.csv', index=False)
all_shops_reviews.to_excel('shops_reviews.xlsx', index=False)
all_shops_reviews.to_parquet('shops_reviews.parquet.gz', index=False, compression='gzip')
