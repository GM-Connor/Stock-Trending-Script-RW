#Stock Trending Script v1.0 /u/RolandWind
from lxml import html
import requests
import time
import datetime
import json

def req(s):
    useTime = time.time()
    useFormat = '%m:%d:%Y'
    #Data based on last x weeks
    weeks = 2
    now = datetime.datetime.fromtimestamp(useTime).strftime(useFormat).split(':')
    then = datetime.datetime.fromtimestamp(useTime-(((weeks * 7) - 1) * 86400)).strftime(useFormat).split(':')
    now[0] = int(now[0]) - 1
    then[0] = int(then[0]) - 1
    #Gets Volume
    give = {'s':s.upper()}
    receive = requests.get('http://finance.yahoo.com/q/',params=give)
    structured = html.fromstring(receive.text)
    volume = int(structured.xpath('//table[@id="table2"]/tr[3]/td/span/text()')[0].replace(',',''))
    #Get Historical Data
    send = {'s':s.upper(),'a':then[0],'b':then[1],'c':then[2],'d':now[0],'e':now[1],'f':now[2],'g':'d'}
    page = requests.get('http://finance.yahoo.com/q/hp',params=send)
    tree = html.fromstring(page.text)
    current = tree.xpath('//table[@class="yfnc_datamodoutline1"]/tr/td/table/tr/td[5]/text()')
    current.reverse()
    for x in range(0,len(current)):
        current[x] = float(current[x])
        x = x + 1
    #Choose Min Volume
    minVol = 250000
    if volume > minVol:
        return current

def percentChange(old,new):
    old = float(old) + .0
    change = ((new * 100) / old)/100
    return change

def match(symbol):
    list1 = req(symbol)
    diff = 0
    record = []
    chosen = ''
    for x in range(0,len(list1)):
        if x != 0:
            pC = percentChange(list1[x-1],list1[x])
            pCM = (pC * 100) - 100
            diff = diff + pCM
            #How stable historical data needs to be (Closer to 0 = more stable, but you don't want it to be too stable) [percentage deviation allowed]
            #Recommended to leave as is
            stability = 5
            if abs(diff) > 5:
                #Minimum days of stability
                minStability = 4
                if (diff > 0) and (len(record) > (minStability - 1)):
                    chosen = record
                record = []
                diff = 0
            else:
                record.append(list1[x-1])
        x = x + 1
    if chosen and not record:
        print symbol.upper() + ' is trending'
        return symbol.upper()
    else:
        print symbol.upper() + ' doesn\'t meet criteria'
        return False

def cycle(symbols):
    good = []
    for s in symbols:
        try:
            #Match Function
            result = match(s)
            if result:
                good.append(result)
        except:
            print '### Low Volume: ' + s.upper()
        f = open('t_time.txt','w')
        f.write(str(time.time()))
        f.close
        print good
    #Saves results when done to file in same folder as script [JSON Format]
    f = open('trending_' + datetime.datetime.fromtimestamp(time.time()).strftime('%m_%d_%Y') + '.json','w')
    f.write(json.dumps(good))
    f.close
    print json.dumps(good)

def main():
    ###Reads from list of symbols
    f = open('symbols.json','r')
    symbols = json.loads(f.read())
    f.close
    #Repeat?
    repeat = True
    #Repeat every x hours
    hours = 24
    if repeat:
        while True:
            now = time.time()
            #Cycle function
            cycle(symbols)
            again = time.time()
            diff = (hours * 3600) - (again - now)
            if diff < 1:
                diff = 1
            time.sleep(diff)
        
main()
