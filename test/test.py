from pyquery import PyQuery as pq

f = open('a.txt', 'r')
r=f.read()
f.close()

doc = pq(r)
main=doc('div#main')
ul=main('ul li').items()
for l in ul:
    hr = l('a').attr('href')
    l('a').attr('title')
    print(l)
    print('/////////')

