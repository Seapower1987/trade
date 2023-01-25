import requests
import json

class ApiError(Exception):
    pass

class cryptoApi:
    def __init__(self, config):
        if type(config) is dict and config['APIURI'] and config['APIKEY']:
            self.config = config
            self.requestObj = {}
        else:
            raise ApiError(f"Api config must be a dictionary")
    
    def test(self, req, data):      #requires 2 args
        if req and data:
            self.requestObj['req'] = req
            self.requestObj['data'] = data
            self.apiRequest('/test', False)
            return True
        else:
            raise ApiError(f"Req or data are undefined. \nreq:{req}, data:{data}")
    
    def getPaares(self, currency=None): #requires no args
        if currency:
            self.requestObj['curr'] = currency
        res = self.apiRequest('/getpaares', True)
        return res
    
    def sendLog(self, data):
        if type(data) is dict:
            self.requestObj['data'] = data
            res = self.apiRequest('/log', False)
            return res
        else:
            raise ApiError(f"Report data must be more than 0 symbol length. \nReport length:{len(data)}")
        
    
    def apiRequest(self, apiRoute, respType):
        self.requestObj['apiKey'] = self.config['APIKEY']
        
        url = self.config['APIURI'] + apiRoute
        payload = json.dumps(self.requestObj)
        headers = {
            'Content-Type': 'application/json'
        }
        
        res = requests.request("POST", url, headers=headers, data=payload)
        
        self.requestObj.clear()
        
        if res.status_code == 200:
            if respType is True:
                return res.json()['data']  
            else:
                return True
        else:
            raise ApiError(f"Server error. {res.text}")