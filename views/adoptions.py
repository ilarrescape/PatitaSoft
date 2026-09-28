from datetime import date
import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit
from core.helpers import options_map,selected_id
from core.ui import header
from core.exporters import export_buttons

def _dogs(): return options_map(fetch_all("select id,name from dogs order by name"))
@st.dialog('Nueva adopción',width='large')
def add_dialog():
    dm=_dogs(); a,b,c=st.columns(3)
    with a: dog=st.selectbox('Perrito',list(dm)); dt=st.date_input('Fecha de adopción',date.today()); name=st.text_input('Adoptante *')
    with b: dni=st.text_input('DNI'); phone=st.text_input('Teléfono'); email=st.text_input('Email')
    with c: address=st.text_input('Domicilio'); city=st.text_input('Ciudad'); follow=st.text_input('Estado seguimiento','Pendiente')
    nextd=st.date_input('Próximo seguimiento',value=None); notes=st.text_area('Notas')
    if st.button('Guardar adopción',type='primary',use_container_width=True):
        if not name: st.warning('Nombre del adoptante obligatorio.'); return
        execute('insert into adoptions(dog_id,adoption_date,adopter_name,adopter_dni,phone,email,address,city,followup_status,followup_date,notes) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(dm[dog],dt,name,dni,phone,email,address,city,follow,nextd,notes)); execute("update dogs set status_category_id=(select id from categories where scope='dog_status' and name='Adoptado' limit 1) where id=%s",(dm[dog],)); st.rerun()
@st.dialog('Editar adopción',width='large')
def edit_dialog(i):
    r=fetch_one('select * from adoptions where id=%s',(i,)); a,b=st.columns(2)
    with a: dt=st.date_input('Fecha',r['adoption_date']); name=st.text_input('Adoptante',r['adopter_name']); dni=st.text_input('DNI',r['adopter_dni'] or ''); phone=st.text_input('Teléfono',r['phone'] or '')
    with b: email=st.text_input('Email',r['email'] or ''); address=st.text_input('Domicilio',r['address'] or ''); city=st.text_input('Ciudad',r['city'] or ''); follow=st.text_input('Seguimiento',r['followup_status'] or '')
    notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute('update adoptions set adoption_date=%s,adopter_name=%s,adopter_dni=%s,phone=%s,email=%s,address=%s,city=%s,followup_status=%s,notes=%s where id=%s',(dt,name,dni,phone,email,address,city,follow,notes,i)); st.rerun()
@st.dialog('Eliminar adopción')
def delete_dialog(i):
    r=fetch_one('select dog_id from adoptions where id=%s',(i,)); st.warning('Se elimina el registro de adopción. El perrito volverá al estado En refugio.')
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from adoptions where id=%s',(i,)); execute("update dogs set status_category_id=(select id from categories where scope='dog_status' and name='En refugio' limit 1) where id=%s",(r['dog_id'],)); st.rerun()
def render():
    header('Adopciones','Perritos adoptados, datos de adoptantes y seguimiento')
    df=fetch_all('select a.id,d.name Perrito,a.adoption_date Fecha,a.adopter_name Adoptante,a.adopter_dni DNI,a.phone Teléfono,a.email Email,a.city Ciudad,a.followup_status Seguimiento,a.followup_date `Próxima fecha` from adoptions a join dogs d on d.id=a.dog_id where a.active=1 order by a.adoption_date desc')
    if can_edit() and st.button('Nueva adopción',icon=':material/favorite:'): add_dialog()
    ev=st.dataframe(df,use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row'); sid=selected_id(ev,df)
    c1,c2=st.columns(2)
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df,'Adopciones')
