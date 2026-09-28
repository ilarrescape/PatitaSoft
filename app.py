from __future__ import annotations
import streamlit as st
from core.db import ensure_schema
from core.auth import login, register, current_user
from core.ui import inject_css, nav_sidebar

st.set_page_config(page_title='PatitaSOFT',page_icon='🐾',layout='wide',initial_sidebar_state='expanded')
inject_css()
try:
    ensure_schema()
except Exception as e:
    st.error('No se pudo conectar/inicializar MySQL. Revisá las variables MYSQL* en Railway o .env/secrets.')
    st.exception(e); st.stop()

def auth_screen():
    a,b,c=st.columns([1,1.1,1])
    with b:
        st.image('assets/logo.png',use_container_width=True)
        tab1,tab2=st.tabs(['Ingresar','Registrarse'])
        with tab1:
            with st.form('login'):
                email=st.text_input('Email'); password=st.text_input('Contraseña',type='password')
                ok=st.form_submit_button('Ingresar',icon=':material/login:',use_container_width=True)
                if ok:
                    if login(email,password): st.rerun()
                    else: st.error('Credenciales inválidas o usuario desactivado.')
        with tab2:
            st.caption('El primer usuario registrado se crea como administrador.')
            with st.form('reg'):
                full=st.text_input('Nombre y apellido'); email=st.text_input('Email',key='re'); p1=st.text_input('Contraseña',type='password',key='rp1'); p2=st.text_input('Repetir contraseña',type='password')
                go=st.form_submit_button('Crear cuenta',icon=':material/person_add:',use_container_width=True)
                if go:
                    if len(full)<3 or '@' not in email or len(p1)<8: st.warning('Completá nombre, email válido y contraseña de al menos 8 caracteres.')
                    elif p1!=p2: st.warning('Las contraseñas no coinciden.')
                    else:
                        try: register(full,email,p1); st.success('Cuenta creada. Ya podés ingresar.')
                        except Exception as ex: st.error(f'No se pudo registrar: {ex}')
if not current_user(): auth_screen(); st.stop()
nav_sidebar()
page=st.session_state.get('page','Dashboard')
modules={
'Dashboard':'views.dashboard','Perritos':'views.dogs','Salud':'views.health','Finanzas':'views.finance','Inventario':'views.inventory',
'Proveedores':'views.partners','Adopciones':'views.adoptions','Castraciones':'views.castrations','Categorías':'views.categories','Usuarios':'views.users'}
mod=__import__(modules.get(page,'views.dashboard'),fromlist=['render']); mod.render()
