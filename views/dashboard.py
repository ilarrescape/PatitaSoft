from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from core.db import fetch_all, scalar
from core.ui import header

def render():
    header('Dashboard','Resumen operativo y administrativo del refugio Patitas')
    dogs=int(scalar("select count(*) from dogs d left join categories c on c.id=d.status_category_id where coalesce(c.name,'') <> 'Adoptado'",default=0) or 0)
    adopted=int(scalar("select count(*) from adoptions where active=1",default=0) or 0)
    income=float(scalar("select coalesce(sum(amount),0) from finance_movements where movement_type='Ingreso'",default=0) or 0)
    expense=float(scalar("select coalesce(sum(amount),0) from finance_movements where movement_type='Gasto'",default=0) or 0)
    cols=st.columns(4)
    labels=[('Perritos actuales',dogs,'🐶'),('Adopciones',adopted,'❤️'),('Ingresos',f'$ {income:,.0f}','💰'),('Gastos',f'$ {expense:,.0f}','🧾')]
    for col,(lab,val,emoji) in zip(cols,labels):
        with col: st.metric(f'{emoji} {lab}',val)
    st.markdown('---')
    fin=fetch_all("select date_format(movement_date,'%Y-%m') mes,movement_type,sum(amount) total from finance_movements group by 1,2 order by 1")
    status=fetch_all("select coalesce(c.name,'Sin estado') estado,count(*) cantidad,coalesce(c.color_hex,'#64748B') color from dogs d left join categories c on c.id=d.status_category_id group by 1,3")
    cas=fetch_all("select month(castration_date) mes_num, date_format(castration_date,'%b') mes, species,count(*) cantidad from castrations where year(castration_date)=year(curdate()) group by 1,2,3 order by 1")
    c1,c2=st.columns(2)
    with c1:
        st.subheader('Ingresos y gastos por mes')
        if len(fin): st.plotly_chart(px.bar(fin,x='mes',y='total',color='movement_type',barmode='group',color_discrete_map={'Ingreso':'#16D7B0','Gasto':'#FF2038'}),use_container_width=True)
        else: st.info('Todavía no hay movimientos financieros.')
    with c2:
        st.subheader('Estado de los perritos')
        if len(status): st.plotly_chart(px.pie(status,names='estado',values='cantidad',hole=.48,color='estado',color_discrete_map={r.estado:r.color for _,r in status.iterrows()}),use_container_width=True)
        else: st.info('Todavía no hay perritos cargados.')
    welfare=fetch_all("select date_format(admission_date,'%Y-%m') mes,count(*) Ingresos from dogs group by 1 order by 1")
    adp=fetch_all("select date_format(adoption_date,'%Y-%m') mes,count(*) Adopciones from adoptions where active=1 group by 1 order by 1")
    c3,c4=st.columns(2)
    with c3:
        st.subheader('Castraciones del año')
        if len(cas): st.plotly_chart(px.bar(cas,x='mes',y='cantidad',color='species',barmode='group',color_discrete_sequence=['#FF9700','#14C8D4']),use_container_width=True)
    with c4:
        st.subheader('Ingresos y adopciones')
        import pandas as pd
        if len(welfare) or len(adp):
            merged=pd.merge(welfare,adp,on='mes',how='outer').fillna(0).sort_values('mes')
            long=merged.melt(id_vars='mes',var_name='Movimiento',value_name='Cantidad')
            st.plotly_chart(px.line(long,x='mes',y='Cantidad',color='Movimiento',markers=True,color_discrete_sequence=['#FF9700','#16D7B0']),use_container_width=True)
    low=fetch_all("select name as Producto,current_stock as Stock,minimum_stock as Mínimo,unit as Unidad from inventory_items where active=1 and current_stock<=minimum_stock order by current_stock")
    if len(low):
        st.warning('Hay productos con stock mínimo o crítico.')
        st.dataframe(low,use_container_width=True,hide_index=True)
