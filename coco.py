import urllib3
import urllib
from bs4 import BeautifulSoup
import re

def cocoScraping(title):
    #baseUrl = 'https://coco.to'

    html = urllib3.PoolManager()
    url = 'https://coco.to/movies?q={}'.format(title)
    encodedUrl = urllib.parse.quote(url,'/:?=&')

    r = html.request('GET', encodedUrl)
    data = r.data.decode('utf-8')

    soup = BeautifulSoup(data,'html.parser')

    idTitle = []
    for element in soup.findAll("div",{"class":"li_pp"}):
            tempId = re.sub(r'\D', '', element.a['href'])
            tempTitle = element.find('div' , {'class': 'li_ttl'} ).string
            idTitle.append({'cocoId': tempId , 'title':tempTitle})
   
    for element in idTitle:
        tempTitle = element['title']
        tempTitle = re.sub(r'\s',' ',tempTitle)

        tempTitle = re.sub(r'（[^（）]*）', "", tempTitle)
    
        tempTitle = re.sub(r'\([^\(\)]*\)', "", tempTitle)
        tempTitle = tempTitle.replace('...','')
        element['title'] = tempTitle
        
    regulatedTitle  = re.sub(r'\s',' ',title)
    regulatedTitle  = re.sub(r'（[^（）]*）', "", regulatedTitle)
    regulatedTitle  = re.sub(r'\([^\(\)]*\)', "", regulatedTitle)
    regulatedTitle = regulatedTitle.replace('...','')
        
    select = None

    for element in idTitle:
        if regulatedTitle[:len(element['title'])] == element['title']:
            select = element
            break

    comments = []

    for i in range(20):
        url = 'https://coco.to/movie/{}/review/{}'.format(select['cocoId'],str(i+1))
        encodedUrl = urllib.parse.quote(url,'/:?=&')
        r = html.request('GET', encodedUrl)
        data = r.data.decode('utf-8')
        soup = BeautifulSoup(data,'html.parser')
        
        flag = False
        
        if len(soup.findAll('h2', {'class':'tweet_title2'})) > 0:
            flag = True
        
        li = soup.findAll('li',{'class':'tweet_li'})
        for counter,each in enumerate(li):
            #if (flag == True) and (counter != 0):
            #    if 'tweet_title2' in  each.previous_sibling.previous_sibling.previous_sibling.previous_sibling['class']:
            #       break
            commentString = each.find('div',{'class':'tweet_text'}).next_element
            processedComment = re.sub(r'\s',' ',commentString)
            comments.append(processedComment)
            
        if flag:
            break
    
    return(comments)