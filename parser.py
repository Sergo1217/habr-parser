import csv
import asyncio
import aiohttp
import os
from datetime import datetime
from bs4 import BeautifulSoup
from sys import argv


class parser:
    def __init__(self, *, links_file='habr.csv', conn_limit=4, headers={}):
        os.mkdir('rez') if not os.path.isdir('rez') else True
        self.links = self.get_links(links_file)
        self.conn_limit = conn_limit
        self.head = headers
        self.ErrorList = []


    def __del__(self):
        with open("notended.csv", "w", newline='') as file:
            spamwriter = csv.DictWriter(file, fieldnames=['url'])
            spamwriter.writeheader()
            for link in self.ErrorList:
                spamwriter.writerow({'url': link})


    def get_links(self, filename):
        links = []
        try:
            with open(filename, 'r', newline='') as csvfile:
                spamreader = csv.DictReader(csvfile)
                for row in spamreader:
                    links.append(row['url'])
            return links
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
            exit()
        except Exception as err:
            print(err)
            exit()


    async def get_page_data(self, session, url):
        try:
            async with session.get(url=url, headers=self.head) as response:
                response_text = await response.text()
                soup = BeautifulSoup(response_text, "lxml")
                name = soup.find(class_="page-title__title")
                with open(os.path.join("rez", f"{url.split('/')[-1]}.txt"), "w", encoding="utf-8") as file:
                    rez = ""
                    if name:
                        rez += name.text + "\n" + url + "\n" + \
                            response_text.replace("\r", "").replace("\n", "")
                        file.write(rez)
                    else:
                        self.ErrorList.append(url)
        except Exception as err:
            print(err)
            self.ErrorList.append(url)


    async def gather_data(self):
        tasks = []
        try:
            conn = aiohttp.TCPConnector(limit=self.conn_limit)
            async with aiohttp.ClientSession(connector=conn) as sassion:
                for url in self.links:
                    task = asyncio.create_task(
                        self.get_page_data(sassion, url))
                    tasks.append(task)
                await asyncio.gather(*tasks)
        except Exception as err:
            print(err)


def main():
    start_time = datetime.now()
    head = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"
    }
    try:
        if len(argv) == 2:
            links_file = argv[1]
            parser1 = parser(links_file=links_file, headers=head)
            asyncio.run(parser1.gather_data())
        elif len(argv) == 3:
            links_file = argv[1]
            conn_limit = int(argv[2])
            parser1 = parser(links_file=links_file,
                             conn_limit=conn_limit, headers=head)
            asyncio.run(parser1.gather_data())
        else:
            parser1 = parser(headers=head)
            asyncio.run(parser1.gather_data())
    except KeyboardInterrupt:
        print('Программа завершена по нажатию')
    except Exception as err:
        print(err)
    finally:
        print(datetime.now() - start_time)


if __name__ == '__main__':
    main()
