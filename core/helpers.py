from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from core.db import fetch_all

def categories(scope):
    df=fetch_all("select id,name,color_hex from categories where scope=%s and active=1 order by name",(scope,))
    return df

def options_map(df,id_col='id',label_col='name'):
    return {str(r[label_col]):int(r[id_col]) for _,r in df.iterrows()}

def selected_id(event, df):
    try:
        rows=event.selection.rows
        return int(df.iloc[rows[0]]['id']) if rows else None
    except Exception: return None

def clean(v):
    if pd.isna(v): return None
    return v

def as_date(v):
    if v is None or pd.isna(v): return None
    if hasattr(v,'date'): return v.date()
    return v


def colored_category_table(df, category_col='Categoría', color_col='Color'):
    """Devuelve un Styler para pintar la celda de categoría con su HEX configurable."""
    if df.empty or category_col not in df.columns or color_col not in df.columns:
        return df
    colors=df[color_col].fillna('#64748B').astype(str).tolist()
    def apply_style(col):
        if col.name != category_col:
            return ['']*len(col)
        return [f'background-color:{c};color:white;font-weight:700;border-radius:8px' for c in colors]
    return df.style.apply(apply_style, axis=0)
