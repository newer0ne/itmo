import streamlit as st
from gsheetsdb import connect
import pandas as pd
import numpy as np
import openpyxl
import io
from io import BytesIO
import os
import csv
from pyxlsb import open_workbook as open_xlsb

st.title('Отчет о выполнении проекта')
st.header('Описание набора данных')
st.write('Набором данных является таблица excel, загруженная на Google диск с настройками общего доступа.'
        'Таблица представляет из себя датасет полученный в результате эксперимента проводимого в рамках кандидатской диссертации.'
        'Кстати меня можно поздравить, 08.02.2022 я защитил кандидатскую диссертацию по направлению 05.02.08 Машиностроение')

# Создаём связь
conn = connect()

# Подготовка к SQL-запросу в Google Sheet.
# Использует метод st.cache для повторного запуска только при изменении запроса или через 600  секунд.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

sheet_url = st.secrets["public_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
tab = pd.DataFrame(rows)
st.write(tab)
