from datetime import date
import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit
from core.helpers import options_map,selected_id
from core.ui import header
from core.exporters import export_buttons

def _dogs(): return options_map(fetch_all('select id,name from dogs order by name'))
def _partners(): return options_map(fetch_all('select id,name from partners where active=1 order by name'))
@st.dialog('Nueva castración',width='large')
def add_dialog():
    dm,pm=_dogs(),_partners(); a,b,c=st.columns(3)
    with a: linked=st.checkbox('Perrito del refugio',True); dog=st.selectbox('Perrito',list(dm),disabled=not linked); ext=st.text_input('Nombre animal externo',disabled=linked)
    with b: species=st.selectbox('Especie',['Perro','Gato']); sex=st.selectbox('Sexo',['Hembra','Macho','Desconocido']); dt=st.date_input('Fecha',date.today())
    with c: vet=st.text_input('Veterinario/a'); partner=st.selectbox('Veterinaria',['—']+list(pm)); cost=st.number_input('Costo',min_value=0.0,step=100.0)
    campaign=st.text_input('Campaña / operativo'); notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True):
        did=dm.get(dog) if linked else None; execute('insert into castrations(dog_id,external_animal_name,species,sex,castration_date,veterinarian,partner_id,campaign,cost,notes) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(did,None if linked else ext,species,sex,dt,vet,pm.get(partner),campaign,cost,notes));
        if did: execute('update dogs set sterilized=1 where id=%s',(did,))
        st.rerun()
@st.dialog('Editar castración',width='large')
def edit_dialog(i):
    r=fetch_one('select * from castrations where id=%s',(i,)); a,b=st.columns(2)
    with a: dt=st.date_input('Fecha',r['castration_date']); vet=st.text_input('Veterinario/a',r['veterinarian'] or ''); campaign=st.text_input('Campaña',r['campaign'] or '')
    with b: cost=st.number_input('Costo',min_value=0.0,value=float(r['cost'])); notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute('update castrations set castration_date=%s,veterinarian=%s,campaign=%s,cost=%s,notes=%s where id=%s',(dt,vet,campaign,cost,notes,i)); st.rerun()
@st.dialog('Eliminar castración')
def delete_dialog(i):
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from castrations where id=%s',(i,)); st.rerun()
def render():
    header('Castraciones','Registro mensual de perros y gatos, propios o externos')
    df=fetch_all("select c.id,coalesce(d.name,c.external_animal_name,'Sin nombre') Animal,c.species Especie,c.sex Sexo,c.castration_date Fecha,c.veterinarian Veterinaria,p.name Organización,c.campaign Campaña,c.cost Costo from castrations c left join dogs d on d.id=c.dog_id left join partners p on p.id=c.partner_id order by c.castration_date desc")
    if can_edit() and st.button('Nueva castración',icon=':material/add:'): add_dialog()
    ev=st.dataframe(df,use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row'); sid=selected_id(ev,df)
    c1,c2=st.columns(2)
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df,'Castraciones')
