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
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import seaborn as sns 
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.title('Отчет о выполнении проекта')
st.header('Описание набора данных')
st.write('Набором данных является таблица excel, загруженная на Google docs (гугл диск) с настройками общего доступа. '
        'Таблица представляет из себя датасет полученный в результате эксперимента проводимого в рамках кандидатской диссертации. '
        'Кстати меня можно поздравить, 08.02.2022 я защитил кандидатскую диссертацию на тему "Повышение эффективности обработки методом электролитно-плазменного полирования на основе ионизационной модели парогазовой оболочки" по направлению 05.02.08 Машиностроение. '
        'Детали доступны по ссылке ниже:')

st.code('https://www.spbstu.ru/science/the-department-of-doctoral-studies/defences-calendar/the-degree-of-candidate-of-sciences/zakharov_sergey_vladimirovich/')

st.write('Вместо скучного MS PowerPoint будем использовать **облачный сервис streamlit.io.**')

st.write('Для корректной загрузки прописываем **requirements.txt** в корне репозитория. Также прописываем желаемые библиотеки с желаемыми стабильными версиями.')
code_requirements =  '''xlrd==2.0.1
openpyxl==3.0.7
pyxlsb==1.0.9
pandas==1.3.1
gsheetsdb
XlsxWriter'''
st.code(code_requirements, language='python')

st.write('В настройках приложения **Settings/Secrets** прописываем ссылку на таблицу в Google docs')
st.code('public_gsheets_url = "https://docs.google.com/spreadsheets/d/15283wiW94FwOmLKu-NcB-Lx6AFzZqrbb/edit?usp=sharing&ouid=112094221269107775969&rtpof=true&sd=true"')

# Создаём связь
conn = connect()

# Подготовка к SQL-запросу в Google Sheet. Использует метод st.cache для повторного запуска только при изменении запроса или через 600  секунд.
@st.cache(ttl=600)

# Не совсем понимаю что делает эта функция в streamlit, такое чувство что вытаскивает списки из SQL-запроса
def run_query(query):
    rows = conn.execute(query, headers=1)
    return rows

# Создаём датасет со ссылки
sheet_url = st.secrets["public_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
tab = pd.DataFrame(rows)
st.write('Наш исходный датасет. T - температура раствора электролита, U - напряжение процесса, j - плотность тока. T и U являются факторами x1 и x2, j является откликом y. Спойлер - мы уверены что зависимость нелинейная, потому что занимаемся этой темой с 2016 года и чтото нам это подсказывает.')
st.write(tab)

st.header('Предварительная обработка данных')
st.write('Подготовка данных не требуется, но попробуем графически отобразить полученные значения:')
st.area_chart(tab)

st.write('Окинем взглядом основные статистики, посчитанные по данному набору данных.')
st.write(tab.describe())

#sns.boxplot(x=class_name, y=column_name, palette="husl", data=tab)
#st.pyplot()

columns = tab.columns.tolist()
class_name = columns[-1]
column_name = st.selectbox("",columns)
st.write("#### Select type of plot: ")
plot_type = st.selectbox("", ["kde","box", "violin","swarm"])
if st.button("Generate"):
        if plot_type == "kde":
                st.write(sns.FacetGrid(tab, hue=class_name, palette="husl", height=6).map(sns.kdeplot, column_name).add_legend())
                st.pyplot()
        if plot_type == "box":
                st.write(sns.boxplot(x=class_name, y=column_name, palette="husl", data=tab))
                st.pyplot(sns.boxplot(x=class_name, y=column_name, palette="husl", data=tab))
        if plot_type == "violin":
                st.write(sns.violinplot(x=class_name, y=column_name, palette="husl", data=tab))
                st.pyplot()
        if plot_type == "swarm":
                st.write(sns.swarmplot(x=class_name, y=column_name, data=tab,color="y", alpha=0.9))
                st.pyplot()
