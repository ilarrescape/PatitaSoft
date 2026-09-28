from __future__ import annotations
import html
import streamlit as st
from core.auth import logout, is_admin

ORANGE='#FF9700'; RED='#FF2038'; NAVY='#092B50'; TEAL='#16D7B0'; CYAN='#14C8D4'; CREAM='#FFFAF3'

def inject_css():
    st.markdown(f"""<style>
    .stApp {{background:linear-gradient(180deg,#fffaf3 0%,#fff 48%,#fff8ef 100%);}}
    [data-testid='stSidebar'] {{background:linear-gradient(180deg,#092b50 0%,#0e416f 100%);}}
    [data-testid='stSidebar'] * {{color:white;}}
    [data-testid='stSidebar'] .stButton button {{border:0;border-radius:12px;font-weight:750;justify-content:flex-start;padding:.65rem .8rem;box-shadow:0 5px 14px #0002;}}
    [data-testid='stSidebar'] .stButton:nth-of-type(4n+1) button {{background:#ff9700;}}
    [data-testid='stSidebar'] .stButton:nth-of-type(4n+2) button {{background:#ff2038;}}
    [data-testid='stSidebar'] .stButton:nth-of-type(4n+3) button {{background:#16d7b0;color:#092b50;}}
    [data-testid='stSidebar'] .stButton:nth-of-type(4n) button {{background:#14c8d4;color:#092b50;}}
    .block-container {{padding-top:1.15rem;max-width:1450px;}}
    div[data-testid='stMetric'] {{background:white;border:1px solid #092b5018;border-radius:18px;padding:16px;box-shadow:0 8px 25px #092b5010;}}
    .ps-title {{font-size:2rem;font-weight:900;color:#092b50;margin-bottom:.1rem}}
    .ps-subtitle {{color:#58708a;margin-bottom:1rem}}
    .chip {{display:inline-block;padding:.23rem .58rem;border-radius:999px;color:white;font-weight:800;font-size:.82rem;margin:.1rem .15rem .1rem 0;box-shadow:0 2px 5px #0002;}}
    </style>""", unsafe_allow_html=True)

def header(title, subtitle=''):
    st.markdown(f"<div class='ps-title'>{html.escape(title)}</div><div class='ps-subtitle'>{html.escape(subtitle)}</div>", unsafe_allow_html=True)

def chip(name,color):
    return f"<span class='chip' style='background:{html.escape(str(color))}'>{html.escape(str(name))}</span>"

def nav_sidebar():
    with st.sidebar:
        st.image('assets/logo.png', use_container_width=True)
        u=st.session_state.get('user',{})
        st.caption(f"{u.get('full_name','')} · {u.get('role','')}")
        items=[
            ('Dashboard',':material/dashboard:'),('Perritos',':material/pets:'),('Salud',':material/medical_services:'),
            ('Finanzas',':material/account_balance_wallet:'),('Inventario',':material/inventory_2:'),('Proveedores',':material/handshake:'),
            ('Adopciones',':material/favorite:'),('Castraciones',':material/content_cut:'),('Categorías',':material/palette:')
        ]
        if is_admin(): items.append(('Usuarios',':material/manage_accounts:'))
        for name,icon in items:
            if st.button(name, icon=icon, use_container_width=True, key='nav_'+name): st.session_state.page=name
        st.divider()
        if st.button('Cerrar sesión', icon=':material/logout:', use_container_width=True):
            logout(); st.rerun()
