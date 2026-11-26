import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.database import db
router=APIRouter(prefix='/api/v1',tags=['Accounts and administration'])
passwords=PasswordHash.recommended()
bearer=HTTPBearer()
def secret():
    s=os.getenv('JWT_SECRET_KEY','')
    if len(s)<32: raise HTTPException(503,'JWT secret not configured')
    return s
class Credentials(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)
class Profile(BaseModel):
    full_name:str=Field(default='',max_length=120)
    organization:str=Field(default='',max_length=160)
    user_type:str=Field(default='Individual User',pattern='^(EV Charging Company|City Planner|Business Owner|Researcher / Analyst|Individual User)$')
class Registration(Credentials,Profile):
    pass
class PasswordChange(BaseModel):
    current_password:str
    new_password:str=Field(min_length=8,max_length=128)
class Site(BaseModel):
    name:str=Field(min_length=1,max_length=200)
    latitude:float=Field(ge=-90,le=90)
    longitude:float=Field(ge=-180,le=180)
class Preferences(BaseModel):
    charger_type:str=Field(pattern='^(Any|Fast|Standard)$')
    coverage_gap:float=Field(ge=0,le=100)
    commercial_facilities:float=Field(ge=0,le=100)
    road_proximity:float=Field(ge=0,le=100)
def user(auth:HTTPAuthorizationCredentials=Depends(bearer),s=Depends(db)):
    try: uid=int(jwt.decode(auth.credentials,secret(),algorithms=['HS256'],options={'require':['exp','sub']})['sub'])
    except (jwt.PyJWTError,ValueError,TypeError): raise HTTPException(401,'Invalid token')
    row=s.execute(text('SELECT id,email,role,full_name,organization,user_type FROM planner_users WHERE id=:id'),{'id':uid}).mappings().first()
    if not row: raise HTTPException(401,'Unknown user')
    return dict(row)
def admin(u=Depends(user)):
    if u['role']!='admin': raise HTTPException(403,'Admin required')
    return u
@router.post('/auth/register',status_code=201)
def register(body:Registration,s=Depends(db)):
    try:
        row=s.execute(text('INSERT INTO planner_users(email,password_hash,full_name,organization,user_type) VALUES (:e,:p,:full_name,:organization,:user_type) RETURNING id,email,role,full_name,organization,user_type'),{'e':body.email.lower(),'p':passwords.hash(body.password),'full_name':body.full_name,'organization':body.organization,'user_type':body.user_type}).mappings().one(); s.commit(); return dict(row)
    except IntegrityError: s.rollback(); raise HTTPException(409,'Email already registered')
@router.post('/auth/login')
def login(body:Credentials,s=Depends(db)):
    row=s.execute(text('SELECT * FROM planner_users WHERE email=:e'),{'e':body.email.lower()}).mappings().first()
    if not row or not passwords.verify(body.password,row['password_hash']): raise HTTPException(401,'Invalid credentials')
    return {'access_token':jwt.encode({'sub':str(row['id']),'exp':datetime.now(timezone.utc)+timedelta(hours=2)},secret(),algorithm='HS256'),'token_type':'bearer'}
@router.get('/auth/me')
def me(u=Depends(user)): return u
@router.get('/shortlist')
def shortlist(u=Depends(user),s=Depends(db)):
    return [dict(r) for r in s.execute(text('SELECT id,name,latitude,longitude FROM planner_shortlist WHERE user_id=:u ORDER BY id'),{'u':u['id']}).mappings()]
@router.post('/shortlist',status_code=201)
def save(body:Site,u=Depends(user),s=Depends(db)):
    r=s.execute(text('INSERT INTO planner_shortlist(user_id,name,latitude,longitude) VALUES (:u,:name,:latitude,:longitude) RETURNING id'),{'u':u['id'],**body.model_dump()}).scalar_one();s.commit();return {'id':r}
@router.delete('/shortlist/{id}')
def remove(id:int,u=Depends(user),s=Depends(db)):
    r=s.execute(text('DELETE FROM planner_shortlist WHERE id=:id AND user_id=:u'),{'id':id,'u':u['id']});s.commit()
    if not r.rowcount: raise HTTPException(404,'Site not found')
    return {'deleted':True}
@router.get('/preferences')
def preferences(u=Depends(user),s=Depends(db)):
    r=s.execute(text('SELECT charger_type,coverage_gap,commercial_facilities,road_proximity FROM planner_preferences WHERE user_id=:u'),{'u':u['id']}).mappings().first()
    return dict(r) if r else {'charger_type':'Any','coverage_gap':40,'commercial_facilities':35,'road_proximity':25}
@router.put('/preferences')
def update_preferences(body:Preferences,u=Depends(user),s=Depends(db)):
    if abs(body.coverage_gap+body.commercial_facilities+body.road_proximity-100)>0.001: raise HTTPException(422,'Weights must total 100')
    s.execute(text('INSERT INTO planner_preferences VALUES (:u,:charger_type,:coverage_gap,:commercial_facilities,:road_proximity) ON CONFLICT(user_id) DO UPDATE SET charger_type=EXCLUDED.charger_type,coverage_gap=EXCLUDED.coverage_gap,commercial_facilities=EXCLUDED.commercial_facilities,road_proximity=EXCLUDED.road_proximity'),{'u':u['id'],**body.model_dump()});s.commit();return body
@router.get('/admin/stations')
def stations(u=Depends(admin),s=Depends(db)):
    return [dict(r) for r in s.execute(text('SELECT * FROM planner_stations ORDER BY id')).mappings()]
@router.post('/admin/stations',status_code=201)
def add_station(body:Site,u=Depends(admin),s=Depends(db)):
    r=s.execute(text('INSERT INTO planner_stations(name,latitude,longitude) VALUES (:name,:latitude,:longitude) RETURNING id'),body.model_dump()).scalar_one();s.commit();return {'id':r}
@router.put('/admin/stations/{id}')
def edit_station(id:int,body:Site,u=Depends(admin),s=Depends(db)):
    r=s.execute(text('UPDATE planner_stations SET name=:name,latitude=:latitude,longitude=:longitude WHERE id=:id'),{'id':id,**body.model_dump()});s.commit()
    if not r.rowcount: raise HTTPException(404,'Station not found')
    return {'updated':True}
@router.delete('/admin/stations/{id}')
def delete_station(id:int,u=Depends(admin),s=Depends(db)):
    r=s.execute(text('DELETE FROM planner_stations WHERE id=:id'),{'id':id});s.commit()
    if not r.rowcount: raise HTTPException(404,'Station not found')
    return {'deleted':True}

@router.put('/auth/profile')
def edit_profile(body:Profile,u=Depends(user),s=Depends(db)):
    row=s.execute(text('UPDATE planner_users SET full_name=:full_name,organization=:organization,user_type=:user_type WHERE id=:id RETURNING id,email,role,full_name,organization,user_type'),{**body.model_dump(),'id':u['id']}).mappings().one();s.commit();return dict(row)
@router.put('/auth/password')
def change_password(body:PasswordChange,u=Depends(user),s=Depends(db)):
    old=s.execute(text('SELECT password_hash FROM planner_users WHERE id=:id'),{'id':u['id']}).scalar_one()
    if not passwords.verify(body.current_password,old): raise HTTPException(400,'Current password is incorrect')
    s.execute(text('UPDATE planner_users SET password_hash=:p WHERE id=:id'),{'p':passwords.hash(body.new_password),'id':u['id']});s.commit();return {'updated':True}
