import json
import urllib.request

# url for coinmarket cap api
url = "https://api.coinmarketcap.com/v1/ticker/litecoin/"

def convert_to_ltc(amount, fiat):
    convert = "?convert={}".format(fiat)
    request = urllib.request.Request(url + convert)
    response = urllib.request.urlopen(request)
    r = response.read()
    cmc = json.loads(r.decode())
    price = float(cmc[0]["price_{}".format(fiat)])
    
    return round(amount / price, 8)


