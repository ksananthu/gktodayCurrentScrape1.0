import bs4
import requests
from urllib import parse
import sqlite3
import logging # tail -f path/app.log
import os

log_file = os.path.join(os.path.dirname(__file__), 'log/log2019.log')
logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s - '
                                                                 '%(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger()

#logger level
logger.setLevel(logging.INFO)

no_of_entries = []
rem = "@import url('https://fonts.googleapis.com/css?family=Open+Sans+Condensed:300,700&display=swap');"

conn = sqlite3.connect('rGktoday.db')
c = conn.cursor()


def getUniqueItems(iterable):
    seen = set()
    result = []
    for item in iterable:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def dynamic_data_entry(ids, day, head, ht, cont):
    id = str(ids)
    date = str(day)
    title = str(head)
    html = str(ht)
    content = str(cont)
    c.execute("INSERT INTO GkData (id, date, title, html, content) VALUES (?, ?, ?, ?, ?)",
              (id, date, title, html, content))
    conn.commit()


# Date function--------------------------------------------------------------
def dateFunction (input):
    x = str(input).replace(',', '')

    years = ['2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']

    sent = x.split()

    dttime = []

    # ---------------------year-------------------------
    for y in years:
        for z in sent:
            # print(z)
            if z.find(y) != -1:
                dttime.append(z)

    # -----------------------month-----------------------
    for i in sent:
        if i.find('Jan') != -1:
            dttime.append('01')
        elif i.find('Feb') != -1:
            dttime.append('02')
        elif i.find('Mar') != -1:
            dttime.append('03')
        elif i.find('Apr') != -1:
            dttime.append('04')
        elif i.find('May') != -1:
            dttime.append('05')
        elif i.find('Jun') != -1:
            dttime.append('06')
        elif i.find('July') != -1:
            dttime.append('07')
        elif i.find('Aug') != -1:
            dttime.append('08')
        elif i.find('Sep') != -1:
            dttime.append('09')
        elif i.find('Oct') != -1:
            dttime.append('10')
        elif i.find('Nov') != -1:
            dttime.append('11')
        elif i.find('Dec') != -1:
            dttime.append('12')

    # -----------------------day-------------------------

    for i in sent:
        if len(i) == 1:
            dttime.append('0' + i)
        elif len(i) == 2:
            dttime.append(i)

    date = ''
    for x in dttime:
        date = date + x

    return date


# --------getting link from archieve----------------------------------------

links = []
res = requests.get('https://currentaffairs.gktoday.com/current-affairs-today-monthly-archives')  # hookup link
logger.info('Begin link =>   https://currentaffairs.gktoday.com/current-affairs-today-monthly-archives')

soup = bs4.BeautifulSoup(res.text, 'html.parser')
for link in soup.find_all('a', href=True):
    id = link['href']
    if id.find('/month/current-affairs') != -1:
        links.append(id)

# years = ['2017']
years = ['2019']
# years = ['2019', '2018', '2017', '2016', '2015', '2014', '2013']
# months = ['jan', 'feb', 'march', 'april', 'may', 'june', 'july', 'august', 'sept', 'oct', 'nov', 'dec']
months = ['dec']

logger.info('Years =>  ' + str(years))
logger.info('Months =>  ' + str(months))

# ---------sorting link by yr,month and removing repeating links----------------
unilinks = []
for x1 in years:
#for x1 in years[::-1]:
    for y in months:
        for x in getUniqueItems(links):
            if x.find(x1) != -1:
                if x.find(y) != -1:
                    unilinks.append(x)
                    #print(x)
                    #print('\n')

# ------------------links for extraction----------------------
for x in unilinks:

    extralinks = []
    extralinks.append(x)

    while True:
        exlen = len(extralinks) - 1
        res2 = requests.get(extralinks[exlen])
        soup2 = bs4.BeautifulSoup(res2.text, 'html.parser')

        # print(soup2.find('a', class_='nextpostslink', href=True))
        exitele = soup2.find('a', class_='nextpostslink', href=True)

        if exitele is not None:
            for link in soup2.find_all('a', class_='nextpostslink', href=True):
                ids = link['href']
                extralinks.append(ids)
                print('\n---------------------------------------------------------------------------------')
                print('Current link =>   ' + extralinks[exlen])
                logger.info('Current link =>   ' + extralinks[exlen])

                print('Next link ====>   ' + str(ids))
                logger.info('Next link ====>   ' + str(ids))

                print('---------------------------------------------------------------------------------\n')


                pf = soup2.findAll("div", class_="post-content")
                pf.pop(0)
                for y in pf:
                    imgs = y.find_all('img')
                    for img in imgs:
                        url = img['src']
                        scheme, netloc, path, params, query, fragment = parse.urlparse(url)
                        new_path = parse.quote(path)
                        new_url = parse.urlunparse((scheme, netloc, new_path, params, query, fragment))
                        img['src'] = new_url

                for y in pf:
                    soup3 = bs4.BeautifulSoup(str(y), 'html.parser')
                    title = soup3.find('h1').text
                    date = soup3.find("span", class_="meta_date").text
                    ids = dateFunction(date)

                    c.execute("SELECT content FROM GkData WHERE (date = '{}') AND (title = '{}')".format(date, title))

                    cont_check = c.fetchall()

                    if len(cont_check) != 0:
                        print('\n*************************************************************************************')
                        print("exists ====> " + str(date) + "   " + str(title))
                        logger.warning("exists ====> " + str(date) + "   " + str(title))

                        print('*************************************************************************************\n')

                    else:
                        print('\n=====================================================================================')
                        no_of_entries.append('1')
                        dynamic_data_entry(ids, date, title, y, str(y.text).replace(rem, " "))
                        # print(str(y.text).replace(rem, " "))
                        print(str(date) + "   " + str(title))
                        logger.info("added ====>  " + str(len(no_of_entries))+ "  "  + str(date) + "   " + str(title))

                        print('=====================================================================================\n')


            continue
        else:
            break

    # getting data from last link from [extralinks]
    print('\n---------------------------------------------------------------------------------')
    print('Last link =>   ' + extralinks[-1])
    logger.info('Last link =>   ' + extralinks[-1])
    print('---------------------------------------------------------------------------------\n')

    res4 = requests.get(extralinks[-1])
    soup4 = bs4.BeautifulSoup(res4.text, 'html.parser')
    pf = soup4.findAll("div", class_="post-content")
    pf.pop(0)
    for y in pf:
        imgs = y.find_all('img')
        for img in imgs:
            url = img['src']
            scheme, netloc, path, params, query, fragment = parse.urlparse(url)
            new_path = parse.quote(path)
            new_url = parse.urlunparse((scheme, netloc, new_path, params, query, fragment))
            img['src'] = new_url

    for y in pf:
        soup4 = bs4.BeautifulSoup(str(y), 'html.parser')
        title = soup4.find('h1').text
        date = soup4.find("span", class_="meta_date").text
        ids = dateFunction(date)

        c.execute("SELECT content FROM GkData WHERE (date = '{}') AND (title = '{}')".format(date, title))

        cont_check2 = c.fetchall()

        if len(cont_check2) != 0:
            print('\n*************************************************************************************')
            print("exists ====> " + str(date) + "   " + str(title))
            logger.warning("exists ====> " + str(date) + "   " + str(title))
            print('*************************************************************************************\n')

        else:
            print('\n=====================================================================================')
            no_of_entries.append('1')
            dynamic_data_entry(ids, date, title, y, str(y.text).replace(rem, " "))
            # print(str(y.text).replace(rem, " "))
            print(str(date) + "   " + str(title))
            logger.info("added ====>  " + str(len(no_of_entries))+ "  "  + str(date) + "   " + str(title))

            print('=====================================================================================\n')


c.close
conn.close()
print('\n -----------------------------------  Done  -------------------------------  ')
print(len(no_of_entries))
logger.info("no of entries added ====>  " + str(len(no_of_entries)))

# requirements pip freeze > requirements.txt


























