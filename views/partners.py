import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit
from core.helpers import categories,options_map,selected_id,colored_category_table
from core.ui import header
from core.exporters import export_buttons

def _types(): return options_map(categories('partner_type'))
@st.dialog('Nueva organización / proveedor',width='large')
def add_dialog():
    tm=_types(); a,b,c=st.columns(3)
    with a: name=st.text_input('Nombre *'); typ=st.selectbox('Tipo',list(tm)); cuit=st.text_input('CUIT')
    with b: contact=st.text_input('Contacto'); phone=st.text_input('Teléfono'); email=st.text_input('Email')
    with c: address=st.text_input('Dirección'); city=st.text_input('Ciudad','Pinamar'); active=st.checkbox('Activo',True)
    notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True):
        if not name: st.warning('El nombre es obligatorio.'); return
        execute("insert into partners(name,partner_type_category_id,contact_name,phone,email,address,city,cuit,notes,active) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,tm.get(typ),contact,phone,email,address,city,cuit,notes,active)); st.rerun()
@st.dialog('Editar organización',width='large')
def edit_dialog(i):
    r=fetch_one('select * from partners where id=%s',(i,)); tm=_types(); cr=fetch_one('select name from categories where id=%s',(r['partner_type_category_id'],)) if r['partner_type_category_id'] else None; names=list(tm); cur=cr['name'] if cr else names[0]
    a,b,c=st.columns(3)
    with a: name=st.text_input('Nombre *',r['name']); typ=st.selectbox('Tipo',names,index=names.index(cur) if cur in names else 0); cuit=st.text_input('CUIT',r['cuit'] or '')
    with b: contact=st.text_input('Contacto',r['contact_name'] or ''); phone=st.text_input('Teléfono',r['phone'] or ''); email=st.text_input('Email',r['email'] or '')
    with c: address=st.text_input('Dirección',r['address'] or ''); city=st.text_input('Ciudad',r['city'] or ''); active=st.checkbox('Activo',bool(r['active']))
    notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute("update partners set name=%s,partner_type_category_id=%s,contact_name=%s,phone=%s,email=%s,address=%s,city=%s,cuit=%s,notes=%s,active=%s where id=%s",(name,tm.get(typ),contact,phone,email,address,city,cuit,notes,active,i)); st.rerun()
@st.dialog('Eliminar organización')
def delete_dialog(i):
    st.warning('Las referencias existentes quedarán sin organización asociada.')
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from partners where id=%s',(i,)); st.rerun()
def render():
    header('Proveedores y organizaciones','Veterinarias, empresas, organizaciones, proveedores y contactos')
    df=fetch_all("select p.id,p.name Nombre,coalesce(c.name,'Sin tipo') Tipo,c.color_hex Color,p.contact_name Contacto,p.phone Teléfono,p.email Email,p.city Ciudad,p.cuit CUIT,if(p.active,'Sí','No') Activo from partners p left join categories c on c.id=p.partner_type_category_id order by p.name")
    if can_edit() and st.button('Nuevo',icon=':material/add:'): add_dialog()
    ev=st.dataframe(colored_category_table(df,category_col='Tipo',color_col='Color'),use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row',column_order=[c for c in df.columns if c!='Color']); sid=selected_id(ev,df)
    c1,c2=st.columns(2)
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df.drop(columns=['Color'],errors='ignore'),'Proveedores y organizaciones')
