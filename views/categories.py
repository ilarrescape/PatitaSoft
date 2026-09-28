import re
import pandas as pd
import streamlit as st
from core.db import fetch_all,execute
from core.auth import can_edit
from core.ui import header,chip
from core.exporters import export_buttons

SCOPES={'dog_status':'Estado de perritos','finance_income':'Ingresos','finance_expense':'Gastos','inventory':'Inventario','health_event':'Salud','partner_type':'Tipo de organización'}
def render():
    header('Categorías y colores','Configurá etiquetas y códigos HEX para mantener una identidad visual consistente')
    scope=st.selectbox('Grupo',list(SCOPES),format_func=lambda x: SCOPES[x])
    df=fetch_all('select id,name,color_hex,active from categories where scope=%s order by name',(scope,))
    if df.empty: df=pd.DataFrame(columns=['id','name','color_hex','active'])
    edited=st.data_editor(df,hide_index=True,use_container_width=True,num_rows='dynamic',disabled=['id'],column_config={'name':st.column_config.TextColumn('Categoría'),'color_hex':st.column_config.TextColumn('Color HEX',help='Ejemplo: #FF9700'),'active':st.column_config.CheckboxColumn('Activa')},key='cat_editor_'+scope)
    st.caption('Vista previa de chips')
    st.markdown(' '.join(chip(r['name'],r['color_hex']) for _,r in edited.iterrows() if r.get('name') and re.match(r'^#[0-9A-Fa-f]{6}$',str(r.get('color_hex','')))),unsafe_allow_html=True)
    if can_edit() and st.button('Guardar categorías',type='primary',icon=':material/save:'):
        for _,r in edited.iterrows():
            name=str(r.get('name','')).strip(); color=str(r.get('color_hex','')).upper().strip(); active=bool(r.get('active',True)); rid=r.get('id')
            if not name: continue
            if not re.match(r'^#[0-9A-F]{6}$',color): st.error(f'Color inválido en {name}: {color}'); return
            if pd.isna(rid): execute('insert into categories(scope,name,color_hex,active) values(%s,%s,%s,%s)',(scope,name,color,active))
            else: execute('update categories set name=%s,color_hex=%s,active=%s where id=%s',(name,color,active,int(rid)))
        st.success('Categorías guardadas.'); st.rerun()
    st.info('Streamlit no permite asignar un HEX distinto a cada opción dentro de una celda editable de st.data_editor. PatitaSOFT guarda el color en MySQL, ofrece edición directa y vista previa como chips; en las vistas se usa el color como identidad de la categoría.')
    export_buttons(df,'Categorías')
