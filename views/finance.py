from datetime import date
import streamlit as st
from core.db import fetch_all,fetch_one,execute
from core.auth import can_edit,current_user
from core.helpers import categories,options_map,selected_id,colored_category_table
from core.ui import header
from core.exporters import export_buttons

def _partner_map(): return options_map(fetch_all("select id,name from partners where active=1 order by name"))
def _cat_map(t): return options_map(categories('finance_income' if t=='Ingreso' else 'finance_expense'))
@st.dialog('Nuevo movimiento',width='large')
def add_dialog():
    c1,c2,c3=st.columns(3)
    with c1: typ=st.selectbox('Tipo',['Ingreso','Gasto']); dt=st.date_input('Fecha',date.today())
    cm=_cat_map(typ); pm=_partner_map()
    with c2: cat=st.selectbox('Categoría',list(cm)); amount=st.number_input('Monto',min_value=0.0,step=100.0)
    with c3: method=st.text_input('Medio de pago'); source=st.text_input('Donante / proveedor')
    desc=st.text_input('Descripción *'); partner=st.selectbox('Empresa/organización', ['—']+list(pm)); receipt=st.text_input('Comprobante / referencia'); notes=st.text_area('Notas')
    if st.button('Guardar',type='primary',use_container_width=True):
        if not desc or amount<=0: st.warning('Descripción y monto mayor a 0 son obligatorios.'); return
        execute("insert into finance_movements(movement_date,movement_type,category_id,description,amount,payment_method,donor_provider,partner_id,receipt_ref,notes,created_by) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(dt,typ,cm.get(cat),desc,amount,method,source,pm.get(partner),receipt,notes,current_user()['id'])); st.rerun()
@st.dialog('Editar movimiento',width='large')
def edit_dialog(i):
    r=fetch_one('select * from finance_movements where id=%s',(i,)); types=['Ingreso','Gasto']; typ=st.selectbox('Tipo',types,index=types.index(r['movement_type'])); cm=_cat_map(typ); pm=_partner_map(); catrow=fetch_one('select name from categories where id=%s',(r['category_id'],)) if r['category_id'] else None
    c1,c2,c3=st.columns(3)
    with c1: dt=st.date_input('Fecha',r['movement_date']); cat=st.selectbox('Categoría',list(cm),index=list(cm).index(catrow['name']) if catrow and catrow['name'] in cm else 0)
    with c2: amount=st.number_input('Monto',min_value=0.0,value=float(r['amount'])); method=st.text_input('Medio de pago',r['payment_method'] or '')
    with c3: source=st.text_input('Donante / proveedor',r['donor_provider'] or ''); receipt=st.text_input('Comprobante',r['receipt_ref'] or '')
    desc=st.text_input('Descripción',r['description']); notes=st.text_area('Notas',r['notes'] or '')
    if st.button('Guardar cambios',type='primary',use_container_width=True): execute("update finance_movements set movement_date=%s,movement_type=%s,category_id=%s,description=%s,amount=%s,payment_method=%s,donor_provider=%s,receipt_ref=%s,notes=%s where id=%s",(dt,typ,cm.get(cat),desc,amount,method,source,receipt,notes,i)); st.rerun()
@st.dialog('Eliminar movimiento')
def delete_dialog(i):
    st.warning('Se eliminará el movimiento seleccionado.')
    if st.button('Eliminar',type='primary',use_container_width=True): execute('delete from finance_movements where id=%s',(i,)); st.rerun()
def render():
    header('Finanzas','Ingresos, donaciones, gastos y trazabilidad de comprobantes')
    df=fetch_all("select f.id,f.movement_date Fecha,f.movement_type Tipo,coalesce(c.name,'Sin categoría') Categoría,c.color_hex Color,f.description Descripción,f.amount Monto,f.payment_method `Medio de pago`,f.donor_provider `Donante / proveedor`,p.name Organización from finance_movements f left join categories c on c.id=f.category_id left join partners p on p.id=f.partner_id order by f.movement_date desc,f.id desc")
    if can_edit() and st.button('Nuevo movimiento',icon=':material/add:',use_container_width=False): add_dialog()
    ev=st.dataframe(colored_category_table(df),use_container_width=True,hide_index=True,on_select='rerun',selection_mode='single-row',column_order=[c for c in df.columns if c!='Color']); sid=selected_id(ev,df)
    c1,c2=st.columns(2)
    if can_edit() and c1.button('Editar',disabled=sid is None,icon=':material/edit:',use_container_width=True): edit_dialog(sid)
    if can_edit() and c2.button('Eliminar',disabled=sid is None,icon=':material/delete:',use_container_width=True): delete_dialog(sid)
    export_buttons(df.drop(columns=['Color'],errors='ignore'),'Finanzas')
