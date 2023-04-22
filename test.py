from bs4 import BeautifulSoup
import requests as req

task_9 = req.get('https://rus-ege.sdamgia.ru/test?category_id=259&filter=all&print=true')

soup = BeautifulSoup(task_9.text, 'lxml')

all_teg = soup.find_all('p')
res = []
tasks = {"task": '',
         "description": '',
         "answer": ''}
for i in all_teg:
    res.append(i.get_text())
res = ''.join(res).split('\xa0')
print(res[:20])
