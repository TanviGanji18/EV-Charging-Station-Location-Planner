import os, math
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

def get_traffic(latitude, longitude):
    key=os.getenv('TOMTOM_API_KEY')
    if not key: raise RuntimeError('Traffic key missing')
    r=requests.get('https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/15/json',params={'key':key,'point':f'{latitude},{longitude}','unit':'kmph'},timeout=(5,20))
    if r.status_code==400 and 'too far' in r.text.lower():
        return {'status':'unavailable','reason':'No supported road segment near point'}
    r.raise_for_status()
    t=r.json()['flowSegmentData']; points=t.get('coordinates',{}).get('coordinate',[])
    def distance(p):
        a,b=math.radians(latitude),math.radians(p['latitude']); d=b-a; e=math.radians(p['longitude']-longitude)
        return 12742000*math.asin(math.sqrt(min(1,math.sin(d/2)**2+math.cos(a)*math.cos(b)*math.sin(e/2)**2)))
    s,f=t.get('currentSpeed'),t.get('freeFlowSpeed')
    return {'status':'success','provider':'TomTom','retrieved_at':datetime.now(timezone.utc).isoformat(),'road_class':t.get('frc'),'current_speed_kmh':s,'free_flow_speed_kmh':f,'slowdown_percent':round(max(0,min(100,100*(1-s/f))),2) if s is not None and f and f>0 else None,'confidence':t.get('confidence'),'road_closure':t.get('roadClosure'),'nearest_coordinate_metres':round(min(map(distance,points)),2) if points else None,'coordinates':points}
