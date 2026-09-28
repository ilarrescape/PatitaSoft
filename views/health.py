from datetime import date
import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit
from core.helpers import categories,options_map,selected_id,colored_category_table
from core.ui import header
from core.exporters import export_buttons

def _dogs(): return options_map(fetch_all('select id,name from dogs order by name'))
def _types(): return options_map(categories('health_event'))
def _partners(): return options_map(fetch_all("select id,name from partners where active=1 order by name"))
@st.dialog('Nuevo registro de salud',width='large')
def add_dialog():
    dm,tm,pm=_dogs(),_types(),_partners(); a,b,c=st.columns(3)
    with a: dog=st.selectbox('Perrito',list(dm)); dt=st.date_input('Fecha',date.today()); typ=st.selectbox('Tipo',list(tm))
    with b: vet=st.text_input('Veterinario/a'); partner=st.selectbox('Veterinaria',['—']+list(pm)); weight=st.number_input('Peso kg',min_value=0.0,step=.1)
    with c: nxt=st.date_input('Próximo control',value=None); medication=st.text_area('Medicación')
    diagnosis=st.text_area('Diagnóstico'); treatment=st.text_area('Tratamiento'); notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True): execute('insert into health_records(dog_id,event_date,event_type_category_id,diagnosis,treatment,medication,veterinarian,partner_id,weight_kg,next_control_date,notes) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(dm[dog],dt,tm[typ],diagnosis,treatment,medication,vet,pm.get(partner),weight or None,nxt,notes)); st.rerun()
@st.dialog('Editar salud',width='large')
def edit_dialog(i):
    r=fetch_one('select * from health_records where id=%s',(i,)); tm=_types(); cr=fetch_one('select name from categories where id=%s',(r['event_type_category_id'],)) if r['event_type_category_id'] else None; names=list(tm); cur=cr['name'] if cr else names[0]
    a,b=st.columns(2)
    with a: dt=st.date_input('Fecha',r['event_date']); typ=st.selectbox('Tipo',names,index=names.index(cur) if cur in names else 0); vet=st.text_input('Veterinario/a',r['veterinarian'] or ''); weight=st.number_input('Peso kg',min_value=0.0,value=float(r['weight_kg'] or 0))
    with b: medication=st.text_area('Medicación',r['medication'] or ''); diagnosis=st.text_area('Diagnóstico',r['diagnosis'] or ''); treatment=st.text_area('Tratamiento',r['treatment'] or ''); notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute('update health_records set event_date=%s,event_type_category_id=%s,veterinarian=%s,weight_kg=%s,medication=%s,diagnosis=%s,treatment=%s,notes=%s where id=%s',(dt,tm[typ],vet,weight or None,medication,diagnosis,treatment,notes,i)); st.rerun()
@st.dialog('Eliminar registro')
def delete_dialog(i):
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from health_records where id=%s',(i,)); st.rerun()
def render():
    header('Salud','Historia clínica, medicación, internaciones y controles')
    df=fetch_all("select h.id,d.name Perrito,h.event_date Fecha,coalesce(c.name,'Sin tipo') Tipo,c.color_hex Color,h.diagnosis Diagnóstico,h.treatment Tratamiento,h.medication Medicación,h.veterinarian Veterinaria,h.weight_kg `Peso kg`,h.next_control_date `Próximo control` from health_records h join dogs d on d.id=h.dog_id left join categories c on c.id=h.event_type_category_id order by h.event_date desc,h.id desc")
    if can_edit() and st.button('Nuevo registro',icon=':material/add:'): add_dialog()
    ev=st.dataframe(colored_category_table(df,category_col='Tipo',color_col='Color'),use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row',column_order=[c for c in df.columns if c!='Color']); sid=selected_id(ev,df)
    c1,c2=st.columns(2)
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df.drop(columns=['Color'],errors='ignore'),'Salud')
