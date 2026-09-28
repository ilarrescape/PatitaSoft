from __future__ import annotations
import os
from contextlib import contextmanager
from pathlib import Path
import mysql.connector
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _cfg():
    try:
        sec = dict(st.secrets.get("mysql", {}))
    except Exception:
        sec = {}
    return {
        "host": sec.get("host") or os.getenv("MYSQLHOST", "localhost"),
        "port": int(sec.get("port") or os.getenv("MYSQLPORT", "3306")),
        "database": sec.get("database") or os.getenv("MYSQLDATABASE", "patitasoft"),
        "user": sec.get("user") or os.getenv("MYSQLUSER", "root"),
        "password": sec.get("password") or os.getenv("MYSQLPASSWORD", ""),
        "autocommit": False,
    }

@contextmanager
def conn():
    c = mysql.connector.connect(**_cfg())
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

def execute(sql, params=None):
    with conn() as c:
        cur=c.cursor()
        cur.execute(sql, params or ())
        return cur.lastrowid

def executemany(sql, seq):
    with conn() as c:
        cur=c.cursor()
        cur.executemany(sql, seq)

def fetch_all(sql, params=None):
    with conn() as c:
        cur=c.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows=cur.fetchall()
        return pd.DataFrame(rows, columns=cur.column_names)

def fetch_one(sql, params=None):
    with conn() as c:
        cur=c.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchone()

def scalar(sql, params=None, default=0):
    row=fetch_one(sql, params)
    if not row: return default
    return next(iter(row.values()))

@st.cache_resource
def ensure_schema():
    path=Path(__file__).resolve().parents[1]/"sql"/"schema.sql"
    raw=path.read_text(encoding="utf-8")
    statements=[s.strip() for s in raw.split(';') if s.strip()]
    with conn() as c:
        cur=c.cursor()
        for stmt in statements:
            cur.execute(stmt)
    return True
