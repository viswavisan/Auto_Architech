from database import sql
import requests,json
from dateutil.tz import gettz
import datetime
import geocoder

def now():return str(datetime.datetime.now(tz=gettz('Asia/Kolkata'))).split('.')[0]

def log_user(user_info,request):
        user=sql.getdata(f"SELECT * FROM Architect.users WHERE name = '{user_info['login']}'")
        ip=request.client.host
        IP = geocoder.ip(ip)
        print(IP)
        latitude = IP.latlng[0] if IP.latlng else None
        longitude = IP.latlng[1] if IP.latlng else None

        response = requests.get(f'https://ipinfo.io/{ip}/json',verify=False)
        location=response.json()
        location_info=json.dumps({'latitude':latitude,'longitude':longitude,'place':location})

        if not user:sql.insert('Architect.users',{'name':user_info['login'], 'password':str(user_info['id']), 'image':user_info['avatar_url'], 'last_login':now(), 'created_date':now(),'location_info':location_info})
        else:sql.update('Architect.users',{'last_login':now(),'location_info':location_info},f"where name='{user_info['login']}'")
