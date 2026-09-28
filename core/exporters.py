from __future__ import annotations
from io import BytesIO
from datetime import datetime
import pandas as pd
import streamlit as st
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def excel_bytes(df:pd.DataFrame, title:str)->bytes:
    out=BytesIO()
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer,index=False,sheet_name='Datos',startrow=3)
        ws=writer.book['Datos']
        ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=max(1,len(df.columns)))
        c=ws.cell(1,1,title); c.font=Font(size=18,bold=True,color='092B50'); c.alignment=Alignment(horizontal='center')
        fills=['FF9700','FF2038','16D7B0','14C8D4']
        for i,cell in enumerate(ws[4],1):
            cell.fill=PatternFill('solid',fgColor=fills[(i-1)%len(fills)]); cell.font=Font(bold=True,color='FFFFFF'); cell.alignment=Alignment(horizontal='center')
        thin=Side(style='thin',color='D8DEE8')
        for row in ws.iter_rows(min_row=4):
            for cell in row: cell.border=Border(bottom=thin); cell.alignment=Alignment(vertical='top')
        for col in ws.columns:
            letter=col[0].column_letter; maxlen=max(len(str(x.value or '')) for x in col[:200]); ws.column_dimensions[letter].width=min(max(maxlen+2,12),42)
        ws.freeze_panes='A5'; ws.auto_filter.ref=ws.dimensions
    return out.getvalue()

def pdf_bytes(df:pd.DataFrame, title:str)->bytes:
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=landscape(A4),rightMargin=18,leftMargin=18,topMargin=18,bottomMargin=18)
    styles=getSampleStyleSheet(); title_style=ParagraphStyle('t',parent=styles['Title'],textColor=colors.HexColor('#092B50'),fontSize=18,spaceAfter=10)
    story=[Paragraph(title,title_style),Paragraph('PatitaSOFT · '+datetime.now().strftime('%d/%m/%Y %H:%M'),styles['Normal']),Spacer(1,10)]
    safe=df.fillna('').astype(str).copy(); max_cols=9
    if safe.shape[1]>max_cols: safe=safe.iloc[:,:max_cols]
    data=[list(safe.columns)]+safe.head(500).values.tolist()
    table=Table(data,repeatRows=1)
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#FF9700')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#D8DEE8')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#FFF8EF')])]))
    story.append(table); doc.build(story); return out.getvalue()

def export_buttons(df,name):
    c1,c2=st.columns(2)
    with c1: st.download_button('Excel',excel_bytes(df,name),file_name=f'{name.lower().replace(" ","_")}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',icon=':material/table_view:',use_container_width=True)
    with c2: st.download_button('PDF',pdf_bytes(df,name),file_name=f'{name.lower().replace(" ","_")}.pdf',mime='application/pdf',icon=':material/picture_as_pdf:',use_container_width=True)
