from __future__ import annotations
import bcrypt
import streamlit as st
from core.db import fetch_one, scalar, execute

def hash_password(password:str)->str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password:str, hashed:str)->bool:
    try: return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception: return False

def register(full_name,email,password):
    count=int(scalar("select count(*) from users", default=0) or 0)
    role='admin' if count==0 else 'operator'
    return execute("insert into users(full_name,email,password_hash,role) values(%s,%s,%s,%s)", (full_name.strip(),email.strip().lower(),hash_password(password),role))

def login(email,password):
    user=fetch_one("select * from users where email=%s and active=1", (email.strip().lower(),))
    if user and verify_password(password,user['password_hash']):
        st.session_state.user={k:v for k,v in user.items() if k!='password_hash'}
        return True
    return False

def logout():
    st.session_state.pop('user',None)
    st.session_state.page='Dashboard'

def current_user(): return st.session_state.get('user')
def is_admin(): return bool(current_user() and current_user().get('role')=='admin')
def can_edit(): return bool(current_user() and current_user().get('role') in ('admin','operator'))
