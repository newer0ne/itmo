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

st.write('**df.boxplot** напрямую тут не работает, но проанализировав выборку становится ясно, что наш эксперимент выполнялся неравномерно. Выбросы по boxplot пока не оценить, поэтому наивно предположим что их нет. А заодно оценим как выглядят данные потыкав разные кнопочки ниже:')
columns = tab.columns.tolist()
class_name = columns[-1]
st.write("#### Выберем колонку для отображения: ")
column_name = st.selectbox("",columns)
st.write("#### Выберем тип отображения: ")
plot_type = st.selectbox("", ["box", "violin","swarm"])
if st.button("Generate"):
        if plot_type == "box":
                st.write(sns.boxplot(x=class_name, y=column_name, palette="husl", data=tab))
                st.pyplot()
        if plot_type == "violin":
                st.write(sns.violinplot(x=class_name, y=column_name, palette="husl", data=tab))
                st.pyplot()
        if plot_type == "swarm":
                st.write(sns.swarmplot(x=class_name, y=column_name, data=tab,color="y", alpha=0.9))
                st.pyplot()

st.write('Стандартизируем данные:')
standard_scaler = StandardScaler()
standard_df = pd.DataFrame(data = standard_scaler.fit_transform(tab), index = tab.index, columns = tab.columns)
standard_df

st.write('Оценим визуально и придём к выводу что график измерения напряжения до сих пор рваный, однако интуитивно данные после стандартизации выглядят приятнее:')
st.area_chart(standard_df)

st.write('**boxplot** здорового человека или что это за точки над плотностью тока? Допустим это результат кривой работы термопары и потому плотность тока от температуры шалит:')
st.write(sns.boxplot(data=standard_df))
st.pyplot()
st.write('Джонни, они на боксплоте! Чертовы глюки!')

st.header('Постановка задачи и построение модели')

st.write('Наша задача — выяснить, могут ли предложенные данные быть разбиты каким-то образом на группы (кластеризованы), '
         'и, в случае утвердительного ответа, определить смысл полученных групп. '
         'Для проведения кластеризации будем использовать метод k-means. Попытаемся определить адекватное число кластеров (изучим диапазон от 1 до 10).')

final_df = tab.copy()
K = range(1, 11)
models = [KMeans(n_clusters = k, random_state = 111, n_init = 100, max_iter = 10000).fit(standard_df) for k in K]
dist = [model.inertia_ for model in models]

plt.figure(figsize=(15,10))
plt.plot(K, dist, marker='o')
plt.xlabel('Число кластеров')
plt.ylabel('Сумма квадратов расстояний')
plt.title('Каменистая осыпь')
st.pyplot()
st.write('Как обычно - **экспонента!** Однако не стоит отчаиваться, я буду доволен, если рассмотрю от 4 до 6 кластеров, однако мы рассмотрим этот датасет в диапазоне кластеров от 3 до 9 как в примере. '
         'Кстати спасибо за пример! :)')

st.write('Произведем кластеризацию для каждого случая и визуализируем полученные результаты:')
for i in range(3,9):
  model = KMeans(n_clusters = i, random_state = 111, n_init = 100, max_iter = 10000)
  model.fit(standard_df)

  final_df[f'{i}_clusters'] = model.labels_

  st.write(final_df.groupby(f'{i}_clusters')[['T','U','j']].mean())

  threedee = plt.figure(figsize=(15,10)).gca(projection='3d')
  threedee.scatter(standard_df["T"], standard_df["U"], standard_df["j"], c = final_df[f'{i}_clusters'], alpha = 1, s =40)
  threedee.set_xlabel('Work')
  threedee.set_ylabel('Price')
  threedee.set_zlabel('Salary')
  threedee.set_title(f'{i+1} Clusters')
  st.pyplot()

st.write('По построенным моделям можно предположить, что датасет надо приводить к трехмерной плоскости и уже для него делать разбиения. '
         ' Но в целом мне больше понравилось разбиение на 4 кластера, оно являются на мой взгляд наиболее удачными и интерпретируемым. '
         'С ростом температуры раствора электролита T уменьшается плотность тока j. Чем ниже температуры раствора электролита T тем заметнее влияние напряжения U. '
         'В диапазоне непряжений U 325-350 наблюдается минимальное значение j для всего температурного диапазоне T. '
         'Какой тут вывод можно сделать?')
st.write('Илюминаты!')
