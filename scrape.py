import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, SessionNotCreatedException
from time import sleep
import json
import datetime

if __name__ == "__main__":
    # edit these three variables
    user = sys.argv[1]
    start = datetime.datetime(2015, 1, 1)  # year, month, day
    end = datetime.datetime(2018, 7, 1)  # year, month, day

    # only edit these if you're having problems
    delay = 0.88  # time to wait on each page load before reading the page
    instantiated = False
    i = 0
    while not instantiated:
        i += 1
        try:
            driver = webdriver.Safari()  # options are Chrome() Firefox() Safari()
            instantiated = True
        except SessionNotCreatedException:
            sleep(15)
            print("Unsuccessful driver instantiation # "+str(i)+" for this user.")


    # don't mess with this stuff
    twitter_ids_filename = 'all_ids.json'
    days = (end - start).days + 1
    id_selector = '.time a.tweet-timestamp'
    tweet_selector = 'li.js-stream-item'
    user = user.lower()
    ids = []

    def format_day(date):
        day = '0' + str(date.day) if len(str(date.day)) == 1 else str(date.day)
        month = '0' + str(date.month) if len(str(date.month)) == 1 else str(date.month)
        year = str(date.year)
        return '-'.join([year, month, day])

    def form_url(since, until):
        p1 = 'https://twitter.com/search?f=tweets&vertical=default&q=from%3A'
        p2 =  user + '%20since%3A' + since + '%20until%3A' + until + 'include%3Aretweets&src=typd'
        return p1 + p2

    def increment_day(date, i):
        return date + datetime.timedelta(days=i)

    for day in range(days):
        d1 = format_day(increment_day(start, 0))
        d2 = format_day(increment_day(start, 1))
        url = form_url(d1, d2)
        print(url)
        print(d1)
        driver.get(url)
        sleep(delay)

        try:
            found_tweets = driver.find_elements_by_css_selector(tweet_selector)
            increment = 10

            while len(found_tweets) >= increment:
                print('scrolling down to load more tweets')
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(delay)
                found_tweets = driver.find_elements_by_css_selector(tweet_selector)
                increment += 10

            print('{} tweets found, {} total'.format(len(found_tweets), len(ids)))

            for tweet in found_tweets:
                try:
                    id = tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                    ids.append(id)
                except StaleElementReferenceException as e:
                    print('lost element reference', tweet)

        except NoSuchElementException:
            print('no tweets on this day')

        start = increment_day(start, 1)


    try:
        with open(twitter_ids_filename) as f:
            all_ids = ids + json.load(f)
            data_to_write = list(set(all_ids))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))
    except FileNotFoundError:
        with open(twitter_ids_filename, 'w') as f:
            all_ids = ids
            data_to_write = list(set(all_ids))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))

    with open(twitter_ids_filename, 'w') as outfile:
        json.dump(data_to_write, outfile)

    print('all done here')
    driver.quit()
