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
