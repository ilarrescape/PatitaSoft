from datetime import date
import streamlit as st
from core.db import fetch_all, fetch_one, execute
from core.auth import can_edit
from core.helpers import categories, options_map, selected_id, colored_category_table
from core.ui import header
from core.exporters import export_buttons

def _status_map(): return options_map(categories('dog_status'))

@st.dialog('Nuevo perrito',width='large')
def add_dialog():
    sm=_status_map(); c1,c2,c3=st.columns(3)
    with c1: name=st.text_input('Nombre *'); sex=st.selectbox('Sexo',['Hembra','Macho','Desconocido']); admission=st.date_input('Fecha de ingreso',date.today())
    with c2: breed=st.text_input('Raza / tipo'); size=st.selectbox('Tamaño',['Pequeño','Mediano','Grande','Desconocido']); status=st.selectbox('Estado',list(sm))
    with c3: age=st.text_input('Edad aproximada'); color=st.text_input('Color'); sterilized=st.checkbox('Castrado/a')
    place=st.text_input('Lugar de rescate'); reason=st.text_input('Motivo de ingreso'); photo=st.text_input('URL de foto (opcional)'); notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True):
        if not name.strip(): st.warning('El nombre es obligatorio.'); return
        execute("insert into dogs(name,sex,approx_age,breed,size,color,status_category_id,admission_date,admission_reason,rescue_place,sterilized,notes,photo_url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,sex,age,breed,size,color,sm.get(status),admission,reason,place,sterilized,notes,photo)); st.rerun()

@st.dialog('Editar perrito',width='large')
def edit_dialog(dog_id):
    r=fetch_one('select * from dogs where id=%s',(dog_id,)); sm=_status_map(); current=fetch_one('select name from categories where id=%s',(r['status_category_id'],)) if r['status_category_id'] else None
    c1,c2,c3=st.columns(3)
    with c1: name=st.text_input('Nombre *',r['name']); sex=st.selectbox('Sexo',['Hembra','Macho','Desconocido'],index=['Hembra','Macho','Desconocido'].index(r['sex'])); admission=st.date_input('Ingreso',r['admission_date'])
    with c2: breed=st.text_input('Raza / tipo',r['breed'] or ''); size=st.selectbox('Tamaño',['Pequeño','Mediano','Grande','Desconocido'],index=['Pequeño','Mediano','Grande','Desconocido'].index(r['size'])); status_names=list(sm); cur=current['name'] if current else status_names[0]; status=st.selectbox('Estado',status_names,index=status_names.index(cur) if cur in status_names else 0)
    with c3: age=st.text_input('Edad aproximada',r['approx_age'] or ''); color=st.text_input('Color',r['color'] or ''); sterilized=st.checkbox('Castrado/a',value=bool(r['sterilized']))
    place=st.text_input('Lugar de rescate',r['rescue_place'] or ''); reason=st.text_input('Motivo de ingreso',r['admission_reason'] or ''); photo=st.text_input('URL foto',r['photo_url'] or ''); notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True):
        execute("update dogs set name=%s,sex=%s,approx_age=%s,breed=%s,size=%s,color=%s,status_category_id=%s,admission_date=%s,admission_reason=%s,rescue_place=%s,sterilized=%s,notes=%s,photo_url=%s where id=%s",(name,sex,age,breed,size,color,sm.get(status),admission,reason,place,sterilized,notes,photo,dog_id)); st.rerun()

@st.dialog('Eliminar perrito')
def delete_dialog(dog_id):
    r=fetch_one('select name from dogs where id=%s',(dog_id,)); st.warning(f"Se eliminará {r['name']} y sus registros relacionados. Esta acción no se puede deshacer.")
    if st.button('Eliminar definitivamente',type='primary',use_container_width=True): execute('delete from dogs where id=%s',(dog_id,)); st.rerun()

def render():
    header('Perritos','Ingreso, identificación, estado y seguimiento general')
    df=fetch_all("select d.id,d.name Nombre,d.sex Sexo,d.approx_age `Edad aprox.`,d.breed Raza,d.size Tamaño,coalesce(c.name,'Sin estado') Estado,c.color_hex `Color categoría`,d.admission_date Ingreso,d.rescue_place `Lugar rescate`,if(d.sterilized,'Sí','No') Castrado from dogs d left join categories c on c.id=d.status_category_id order by d.id desc")
    top=st.columns([1,1,1,3])
    if can_edit() and top[0].button('Nuevo',icon=':material/add:',use_container_width=True): add_dialog()
    event=st.dataframe(colored_category_table(df,category_col='Estado',color_col='Color categoría'),use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row',key='dogs_table',column_order=[c for c in df.columns if c!='Color categoría'])
    sid=selected_id(event,df)
    c1,c2,c3=st.columns([1,1,1])
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df.drop(columns=['Color categoría'],errors='ignore'),'Perritos')
