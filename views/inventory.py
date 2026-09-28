from datetime import date
import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit,current_user
from core.helpers import categories,options_map,selected_id,colored_category_table
from core.ui import header
from core.exporters import export_buttons

def _cats(): return options_map(categories('inventory'))
def _partners(): return options_map(fetch_all('select id,name from partners where active=1 order by name'))
@st.dialog('Nuevo producto',width='large')
def add_dialog():
    cm=_cats(); pm=_partners(); a,b,c=st.columns(3)
    with a: name=st.text_input('Producto *'); cat=st.selectbox('Categoría',list(cm)); unit=st.text_input('Unidad','unidad')
    with b: stock=st.number_input('Stock actual',0.0,step=1.0); minimum=st.number_input('Stock mínimo',0.0,step=1.0); exp=st.date_input('Vencimiento',value=None)
    with c: brand=st.text_input('Marca'); concentration=st.text_input('Concentración'); location=st.text_input('Ubicación')
    partner=st.selectbox('Proveedor',['—']+list(pm)); notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True):
        if not name: st.warning('Nombre obligatorio.'); return
        execute("insert into inventory_items(name,category_id,unit,current_stock,minimum_stock,brand,concentration,expiration_date,location,partner_id,notes) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,cm.get(cat),unit,stock,minimum,brand,concentration,exp,location,pm.get(partner),notes)); st.rerun()
@st.dialog('Registrar movimiento de stock',width='large')
def movement_dialog(i):
    r=fetch_one('select name,current_stock from inventory_items where id=%s',(i,)); st.info(f"{r['name']} · stock actual: {r['current_stock']}")
    a,b,c=st.columns(3)
    with a: typ=st.selectbox('Movimiento',['Entrada','Salida','Ajuste']); dt=st.date_input('Fecha',date.today())
    with b: qty=st.number_input('Cantidad',min_value=0.01,step=1.0)
    with c: reason=st.text_input('Motivo')
    if st.button('Aplicar',type='primary',use_container_width=True):
        cur=float(r['current_stock']); new=qty if typ=='Ajuste' else cur+qty if typ=='Entrada' else cur-qty
        if new<0: st.error('El stock no puede quedar negativo.'); return
        execute('insert into inventory_movements(item_id,movement_date,movement_type,quantity,reason,created_by) values(%s,%s,%s,%s,%s,%s)',(i,dt,typ,qty,reason,current_user()['id'])); execute('update inventory_items set current_stock=%s where id=%s',(new,i)); st.rerun()
@st.dialog('Editar producto',width='large')
def edit_dialog(i):
    r=fetch_one('select * from inventory_items where id=%s',(i,)); cm=_cats(); cr=fetch_one('select name from categories where id=%s',(r['category_id'],)) if r['category_id'] else None; names=list(cm); cur=cr['name'] if cr else names[0]
    a,b,c=st.columns(3)
    with a: name=st.text_input('Producto',r['name']); cat=st.selectbox('Categoría',names,index=names.index(cur) if cur in names else 0); unit=st.text_input('Unidad',r['unit'])
    with b: minimum=st.number_input('Stock mínimo',0.0,value=float(r['minimum_stock'])); brand=st.text_input('Marca',r['brand'] or '')
    with c: concentration=st.text_input('Concentración',r['concentration'] or ''); location=st.text_input('Ubicación',r['location'] or ''); active=st.checkbox('Activo',bool(r['active']))
    notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute('update inventory_items set name=%s,category_id=%s,unit=%s,minimum_stock=%s,brand=%s,concentration=%s,location=%s,active=%s,notes=%s where id=%s',(name,cm.get(cat),unit,minimum,brand,concentration,location,active,notes,i)); st.rerun()
@st.dialog('Eliminar producto')
def delete_dialog(i):
    st.warning('También se eliminará su historial de movimientos de stock.')
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from inventory_items where id=%s',(i,)); st.rerun()
def render():
    header('Inventario','Medicamentos, alimento e insumos necesarios para los perritos')
    df=fetch_all("select i.id,i.name Producto,coalesce(c.name,'Sin categoría') Categoría,c.color_hex Color,i.concentration Concentración,i.current_stock Stock,i.minimum_stock Mínimo,i.unit Unidad,i.expiration_date Vencimiento,i.brand Marca,i.location Ubicación,p.name Proveedor,if(i.current_stock<=i.minimum_stock,'CRÍTICO','OK') Estado from inventory_items i left join categories c on c.id=i.category_id left join partners p on p.id=i.partner_id where i.active=1 order by Estado desc,i.name")
    if can_edit() and st.button('Nuevo producto',icon=':material/add:'): add_dialog()
    ev=st.dataframe(colored_category_table(df),use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row',column_order=[c for c in df.columns if c!='Color']); sid=selected_id(ev,df)
    c1,c2,c3=st.columns(3)
    if can_edit() and c1.button('Movimiento',disabled=sid is None,icon=':material/swap_vert:',use_container_width=True): movement_dialog(sid)
    if can_edit() and c2.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c3.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df.drop(columns=['Color'],errors='ignore'),'Inventario')
    with st.expander('Historial de movimientos de stock'):
        hist=fetch_all("select m.id,m.movement_date Fecha,i.name Producto,m.movement_type Tipo,m.quantity Cantidad,m.reason Motivo from inventory_movements m join inventory_items i on i.id=m.item_id order by m.movement_date desc,m.id desc")
        st.dataframe(hist,use_container_width=True,hide_index=True)
        export_buttons(hist,'Movimientos de stock')
