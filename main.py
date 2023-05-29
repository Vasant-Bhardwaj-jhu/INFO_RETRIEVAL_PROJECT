from math import log

import selenium
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import chromedriver_binary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from datetime import datetime

global price_alter
global review_alter
global date_alter
global ISBN
global pref_store

global first_name
global last_name
global street_address
global amazon_email_or_phone
global amazon_password

# Introduction to Statistical Learning: 978-1461471370
# Data Engineering with AWS: 978-1800560413
# Deep Learning (Adaptive Computation and Machine Learning series): 978-0262035613


def weight_calc(date, cost, reviews, numrev, company, bookcondition = "New"):
    weight = 0
    weight += cost * (6-price_alter)

    print(type(reviews))
    print(type(numrev))

    print(reviews)
    print(numrev)

    n = (int(reviews) * int(numrev)) * (6-review_alter)
    if n > 0:
        weight = weight - log(n)

    today = date.today()
    bookcondweight = calc_condition(bookcondition)
    day_diff = num_of_days(date, today)
    weight = weight + (day_diff) * (6-date_alter)
    if pref_store in company:
        weight = weight / 5
    return weight

def calc_condition(cond):
    if "New" in cond:
        return 5
    elif "Good" in cond:
        return 4
    elif "Used" in cond:
        return 3
    else:
        return 1

def num_of_days(date1, date2):
    return (date2-date1).days

class weightedDoc:
    company: str
    seller_name : str
    cost: float
    date : datetime
    reviews : int
    numrev : int
    quality : str
    sellerAddToCart: selenium.webdriver.remote.webelement.WebElement
    weight : int


    def __init__(self, company, cost, date, reviews = None, numrev = None, seller_name = "", sellerAddToCart = None, quality = "New"):
        self.company = company
        self.cost = cost
        self.date = date
        self.reviews = reviews
        self.numrev = numrev
        self.seller_name = seller_name
        self.sellerAddToCart = sellerAddToCart
        self.quality = quality

        self.weight = weight_calc(self.date, self.cost, self.reviews, self.numrev,self.company, self.quality)

    def setWeight(self):
        if self.company == "Barnes&Noble":
            weight = weight_calc(self.date, self.cost, self.reviews, self.numrev, self.company)


# For each book
# Retrieve information from Amazon,Barnes and Noble, Powells(price, reviews, availability, etc.)
# Compute the most favorable one using a custom metric
# Order the book online using selenium


options = webdriver.ChromeOptions()
options.add_argument('--headless')

# Getting data from Amazon
wd = webdriver.Chrome()

wd.implicitly_wait(10)
wd.get("https://www.amazon.com/")


# search_bar = wd.find_element(by=By.XPATH, value="/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[2]/div[1]/input")
# time.sleep(5)
# search_bar.send_keys("978-1071614174")
# time.sleep(5)
# search_button = wd.find_element(by=By.XPATH, value="/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[3]/div/span/input")
# search_button.click()
# time.sleep(15)


def get_books_barnes_and_noble():
    wd.execute_script("window.open('');")
    wd.switch_to.window(wd.window_handles[1])

    wd.get("https://www.barnesandnoble.com/")
    search_bar = wd.find_element(by=By.XPATH,
                                 value="/html/body/div[1]/header/nav/div/div[3]/form/div/div[2]/div/input[1]")
    time.sleep(5)
    search_bar.send_keys(ISBN)
    time.sleep(5)
    search_button = wd.find_element(by=By.XPATH, value="/html/body/div[1]/header/nav/div/div[3]/form/div/span/button")
    search_button.click()
    time.sleep(7)

    #name = wd.find_element(by=By.XPATH,
                           #value='/html/body/main/div[3]/div[1]/section/div[2]/div/div[3]/div[1]/header/div/h1')
    #product_name = name.text

    # find price
    price = wd.find_element(by=By.XPATH, value='.//span[@id="pdp-cur-price"]').text
    product_price = float(price[1:])

    deliveryDay = wd.find_element(By.XPATH, './/*[@id="commerce-zone"]/div[2]/div[3]/div/span[2]/span').text

    if ", " in deliveryDay:
        deliveryDate = (deliveryDay.split(', '))[1]
    else:
        deliveryDate = deliveryDay

    formattedDateTime = datetime.strptime(deliveryDate, '%b %d')

    Barnes_And_Noble_book = weightedDoc("Barnes&Noble", product_price, formattedDateTime, 0, 0, None, None, "New")
    time.sleep(5)
    wd.switch_to.window(wd.window_handles[0])
    return Barnes_And_Noble_book


def barnes_and_noble_add_to_cart():
    wd.switch_to.window(wd.window_handles[1])

    addToCartButton = wd.find_element(By.XPATH, '//*[@id="skuSelection"]/div[1]/form/input[5]')
    #addToCartButton = wait(wd, 20).until(
        #EC.element_to_be_clickable((By.XPATH, '//*[@id="skuSelection"]/div[1]/form/input[5]')))
    addToCartButton.send_keys("\n")
    # addToCartButton.click()

    time.sleep(10)

    try:
        closeAd = wd.find_element(By.XPATH, '/html/body/div[33]/div/div/div[1]/a')
        closeAd.click()
    except:
        print("No ad encountered")

    cartButton = wd.find_element(By.XPATH, '//*[@id="viewShoppingBag"]')
    cartButton.click()

    time.sleep(10)

    # checkoutButton = wd.find_element(By.XPATH, '//*[@id="checkoutForm"]/a')
    # checkoutButton.click()

    time.sleep(5)

    # shoppingCartButton = wd.find_element(By.XPATH, '//*[@id="rhf_header_element"]/nav/div/div[3]/ul/li[2]')
    # shoppingCartButton.click();

    # time.sleep(5)

    # continueToCheckout = wd.find_element(By.XPATH, '//*[@id="checkoutForm"]/a')
    # continueToCheckout.click()


def checkout_barnes_and_noble():
    wd.switch_to.window(wd.window_handles[1])

    wd.get('https://www.barnesandnoble.com/checkout/guest-checkout.jsp')

    time.sleep(5)

    firstNameBox = wd.find_element(By.XPATH, '//*[@id="firstName"]')
    lastNameBox = wd.find_element(By.XPATH, '//*[@id="lastName"]')
    streetAddressBox = wd.find_element(By.XPATH, '//*[@id="streetAddress"]')

    firstNameBox.send_keys(first_name)
    lastNameBox.send_keys(last_name)
    streetAddressBox.send_keys(street_address)

    time.sleep(5)

    # print(product_name)
    # print(product_price)
    # print(deliveryDate)

    wd.switch_to.window(wd.window_handles[0])


def get_books_amazon():
    Books_found = []

    search_bar = wd.find_element(by=By.XPATH,
                                 value="/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[2]/div[1]/input")
    time.sleep(5)
    search_bar.send_keys(ISBN)
    time.sleep(5)
    search_button = wd.find_element(by=By.XPATH,
                                    value="/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[3]/div/span/input")
    search_button.click()
    time.sleep(15)

    product_name = []
    # product_asin = []
    product_price = []
    # product_ratings = []
    # product_ratings_num = []
    product_link = []

    items_all = wait(wd, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
    try:
        items_sponsored = wait(wd, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "AdHolder")]')))
        items = [item for item in items_all if item not in items_sponsored]
    except:
        items = items_all

    for item in items:
        # find name
        name = item.find_element(by=By.XPATH, value='.//span[@class="a-size-medium a-color-base a-text-normal"]')
        product_name.append(name.text)

        # find ASIN number
        # data_asin = item.get_attribute("data-asin")
        # product_asin.append(data_asin)

        # find price
        whole_price = item.find_elements(by=By.XPATH, value='.//span[@class="a-price-whole"]')
        fraction_price = item.find_elements(by=By.XPATH, value='.//span[@class="a-price-fraction"]')

        if whole_price != [] and fraction_price != []:
            price = '.'.join([whole_price[0].text, fraction_price[0].text])
        else:
            price = 0
        product_price.append(price)

        # find ratings box
        ratings_box = item.find_elements(by=By.XPATH, value='.//div[@class="a-row a-size-small"]/span')

        # find ratings and ratings_num
        # if ratings_box != []:
        # ratings = ratings_box[0].get_attribute('aria-label')
        # ratings_num = ratings_box[1].get_attribute('aria-label')
        # else:
        # ratings, ratings_num = 0, 0

        # product_ratings.append(ratings)
        # product_ratings_num.append(str(ratings_num))

        # find link
        link = item.find_element(by=By.XPATH,
                                 value='.//*[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute(
            "href")
        product_link.append(link)

    wd.get(product_link[0])

    all_sellers_button = wd.find_element(By.XPATH, '//*[@id="a-autoid-2"]/span')
    all_sellers_button.click()

    time.sleep(5)

    see_more_button = wd.find_element(By.XPATH, '//*[@id="aod-pinned-offer-show-more-link"]')
    see_more_button.click()

    # time.sleep(3)

    pinned_offer = wd.find_element(By.XPATH, '//*[@id="aod-pinned-offer"]')
    main_seller_object_info = pinned_offer.find_element(By.XPATH, '//*[@id="aod-pinned-offer-additional-content"]')
    main_seller_name = main_seller_object_info.find_element(By.XPATH,
                                                            './/*[@id="aod-offer-shipsFrom"]/div/div/div[2]/span').text

    try:
        main_seller_ratings_text = main_seller_object_info.find_element(By.XPATH,
                                                                        './/*[@id="seller-rating-count-{iter}"]/span').text
        main_seller_rating = main_seller_ratings_text.split("%")[0][-2:]
        main_num_ratings = main_seller_ratings_text.split(" ")[0][1:]
    except:
        main_seller_rating = 0
        main_num_ratings = 0

    main_seller_delivery_day = pinned_offer.find_element(By.XPATH,
                                                         './/*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/span').text
    if ", " in main_seller_delivery_day:
        main_seller_delivery_day = (main_seller_delivery_day.split(', '))[1]

    if " - " in main_seller_delivery_day:
        main_seller_delivery_day = (main_seller_delivery_day.split(' - '))[0]
    main_seller_delivery_day_formatted = datetime.strptime(main_seller_delivery_day, '%b %d')
    # main_seller_delivery_date = main_seller_delivery_day.split(', ')[1]
    main_seller_add_cart = pinned_offer.find_element(By.XPATH, './/*[@id="a-autoid-2-offer-0"]/span/input')
    # main_seller_add_cart.click()
    main_whole_price = pinned_offer.find_elements(by=By.XPATH, value='.//span[@class="a-price-whole"]')
    main_fraction_price = pinned_offer.find_elements(by=By.XPATH, value='.//span[@class="a-price-fraction"]')

    if main_whole_price != [] and main_fraction_price != []:
        main_sellerPrice = '.'.join([main_whole_price[0].text, main_fraction_price[0].text])
    else:
        main_sellerPrice = 0

    ## ADD QUALITY FIELD ##
    main_seller_quality = "New"
    # print("Main Seller Name: " + main_seller_name)
    # print("Main Seller Delivery: " + main_seller_delivery_day)
    # print("Main Seller Rating: " + main_seller_rating)
    # print("Main Seller Num Ratings: " + main_num_ratings)
    # print("Main Seller Price: " + main_sellerPrice)

    Books_found.append(weightedDoc("Amazon", float(main_sellerPrice), main_seller_delivery_day_formatted, main_seller_rating,
                                       main_num_ratings,main_seller_name,main_seller_add_cart, main_seller_quality))

    time.sleep(5)

    all_other_sellers = wait(wd, 50).until(EC.presence_of_all_elements_located((By.ID, 'aod-offer')))

    for seller in all_other_sellers:

        sellerNameObject = seller.find_element(By.XPATH,
                                               './/*[@id="aod-offer-shipsFrom"]/div[@class="a-fixed-left-grid"]/div[@class="a-fixed-left-grid-inner"]/div[@class="a-fixed-left-grid-col a-col-right"]/span')
        sellerName = sellerNameObject.text
        # print("Seller Name: " + sellerName)

        whole_price = seller.find_elements(by=By.XPATH, value='.//span[@class="a-price-whole"]')
        fraction_price = seller.find_elements(by=By.XPATH, value='.//span[@class="a-price-fraction"]')

        if whole_price != [] and fraction_price != []:
            sellerPrice = '.'.join([whole_price[0].text, fraction_price[0].text])
        else:
            sellerPrice = 0
        # print("Seller Price: " + sellerPrice)

        dayObject = seller.find_element(By.XPATH,
                                        './/*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/span[@class="a-text-bold"]')
        day = dayObject.text
        if ", " in day:
            day = (day.split(', '))[1]

        if " - " in day:
            day = (day.split(' - '))[0]
        # date = day.split(' ')[1]
        # print("Delivery date= " + day)
        formattedDay = datetime.strptime(day, '%B %d')

        try:
            sellerRatingObject = seller.find_element(By.XPATH,
                                                     './/*[@id="aod-offer-seller-rating"]/span[@class="a-size-small a-color-base"]/span')
            sellerRatingText = sellerRatingObject.text
            sellerRatingText.replace('\n', '')
            sellerRating = sellerRatingText.split("%")[0][-2:]
            numRatings = sellerRatingText.split(" ")[0][1:]
            # sellerRatingPercent = sellerRatingText.split("%")[0]
        except:
            sellerRatingText = None
            sellerRating = 0
            numRatings = 0

        # print("Seller Rating: " + sellerRating)
        # print("Num Ratings: " + numRatings)

        sellerBookStatusObject = seller.find_element(By.XPATH, './/*[@id="aod-offer-heading"]')
        sellerBookStatus = sellerBookStatusObject.text
        # print("Book condition: " + sellerBookStatus)

        addToCartButtonObject = seller.find_element(By.XPATH,
                                                    './/*[@class="a-button a-button-primary aod-atc-generic-btn-desktop"]/span/input')
        #print(type(addToCartButtonObject))
        # STORE THE aria-label string
        # to find the add to cart button
        # print(addToCartButtonObject.get_attribute('aria-label'))

        # addToCartButtonObject.click()

        # print("\n")

        time.sleep(3)
        Books_found.append(weightedDoc("Amazon", float(sellerPrice), formattedDay, int(sellerRating),
                                       int(numRatings), sellerName, addToCartButtonObject, sellerBookStatus))

    time.sleep(5)
    return Books_found


def checkout_amazon():
    closeOtherSellers = wd.find_element(By.XPATH, '//*[@id="aod-close"]/span/span/i')
    closeOtherSellers.click()

    # wd.get('https://www.amazon.com/gp/cart/view.html?ref_=nav_cart')
    cartButton = wd.find_element(By.XPATH, '//*[@id="nav-cart-count-container"]')
    #cartButton.send_keys('\n')
    cartButton.click()

    time.sleep(5)

    proceedToCheckout = wd.find_element(By.XPATH, '//*[@id="sc-buy-box-ptc-button"]/span/input')
    proceedToCheckout.click()

    time.sleep(5)

    signInBox = wd.find_element(By.XPATH, '//*[@id="ap_email"]')
    signInBox.send_keys(amazon_email_or_phone)
    signInContinueButton = wd.find_element(By.XPATH, '//*[@id="continue"]')
    signInContinueButton.click()

    time.sleep(5)

    passwordBox = wd.find_element(By.XPATH, '//*[@id="ap_password"]')
    passwordBox.send_keys(amazon_password)
    passwordSignInButton = wd.find_element(By.XPATH, '//*[@id="signInSubmit"]')
    passwordSignInButton.click()

    time.sleep(15)

    wd.quit()

if __name__ == "__main__":
    # price_alter = input("on a scale from 0 to 5, how important is price to you?")
    # review_alter = input("on a scale from 0 to 5, how important are reviews to you?")
    # date_alter = input("on a scale from 0 to 5, how important is date to you?")
    # pref_store = input("which company do you prefer more, Amazon or Barnes and Noble? (write Amazon or Barnes below)")

    # Enter your user details here
    first_name = "Saketh"
    last_name = "Manda"
    street_address = "3700 North Charles St"
    amazon_email_or_phone = 'smanda2@jhu.edu'
    amazon_password = ''

    # used to alter the weights of values for user preference, ran into issues implementing this using the terminal
    pref_store = ""   # ALTER THIS TO CHANGE THE PREFERRED STORE
    price_alter = 0         # ALTER THIS TO CHANGE THE IMPORTANCE OF PRICE (from 0 to 5)
    review_alter = 5        # ALTER THIS TO CHANGE THE IMPORTANCE OF REVIEWS (from 0 to 5)
    date_alter = 0          # ALTER THIS TO CHANGE THE IMPORTANCE OF THE DELIVERY DATE (from 0 to 5)
    ISBN = "978-1800560413" # ALTER THIS TO CHANGE THE BOOK BEING SEARCHED FOR
    # SAMPLE ISBNS BELOW:
    # Data Engineering with AWS: 978-1800560413
    # Introduction to Statistical Learning: 978-1461471370

    allBooks = []
    Book1 = get_books_barnes_and_noble()
    #if pref_store == "Barnes":
    #    barnes_and_noble_add_to_cart()
    #    checkout_barnes_and_noble()
    #    exit()
    allBooks.append(Book1)
    Amazon_Books = get_books_amazon()
    allBooks = allBooks + Amazon_Books
    allBooks.sort(key=lambda x:x.weight)
    for books in allBooks:
        print(books.company, books.date, books.cost, books.numrev, books.reviews,
              books.company, books.quality, books.weight, "\n")

    bookToBuy = allBooks[0]
    print(bookToBuy.company, bookToBuy.date, bookToBuy.cost, bookToBuy.numrev, bookToBuy.reviews, bookToBuy.company,
          bookToBuy.quality, bookToBuy.weight, "\n")

    if (bookToBuy.company == "Amazon"):
        bookToBuy.sellerAddToCart.click()
        checkout_amazon()
    else:
        barnes_and_noble_add_to_cart()
        checkout_barnes_and_noble()

#weights: 0 price, 5 reviews, 0 delivery date for 978-1800560413 yielded:
# Amazon 1900-05-27 00:00:00 44.12 930704 90 Amazon New 267540.47649376164

