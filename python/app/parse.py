from lxml import etree
import re

def csstext(e):
    for br in e.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    t = etree.tostring(e, method='text', encoding='utf8').strip()    
    t = t.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    return re.sub(' +',' ', t)

def dumpit(html, filename = 'dumpit.html'):
    print 'dumpit:', html, len(html), filename
    try:
        df = open(filename, 'w')
        df.write(etree.tostring(html))
        df.close()
    except Exception as e:
        print 'dumpit exception:', e
    return html

def html(txt):
    return etree.HTML(txt) 