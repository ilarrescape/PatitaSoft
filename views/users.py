import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import is_admin
from core.helpers import selected_id
from core.ui import header
from core.exporters import export_buttons
@st.dialog('Editar usuario')
def edit_dialog(i):
    r=fetch_one('select * from users where id=%s',(i,)); roles=['admin','operator','viewer']; role=st.selectbox('Rol',roles,index=roles.index(r['role'])); active=st.checkbox('Activo',bool(r['active']))
    if st.button('Guardar',type='primary',use_container_width=True): execute('update users set role=%s,active=%s where id=%s',(role,active,i)); st.rerun()
def render():
    header('Usuarios','Roles y acceso al sistema')
    if not is_admin(): st.error('Solo administradores.'); return
    df=fetch_all("select id,full_name Nombre,email Email,role Rol,if(active,'Sí','No') Activo,created_at `Creado el` from users order by full_name")
    ev=st.dataframe(df,use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row'); sid=selected_id(ev,df)
    if st.button('Editar usuario',disabled=sid is None,icon=':material/edit:'): edit_dialog(sid)
    export_buttons(df,'Usuarios')
