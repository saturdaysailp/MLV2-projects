# -*- coding: utf-8 -*-
"""CasosPositivosCOVID19.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-oHRNTgDTYspJWklF4O_PDAlAQJidT3-
"""

pip install pmdarima

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from google.colab import files
from PIL import Image
uploaded = files.upload()

"""####Lectura de datos"""

data = pd.read_csv("https://raw.githubusercontent.com/Falken777/casos_confirmados_global/main/time_series_covid19_confirmed_global2.csv")
print("Tamaño del df", data.shape)
data.head()

data.drop(columns=["Province/State"], inplace=True)

data.isnull().sum()

"""####Hacemos limpieza de datos"""

data = data.dropna()
print("Tamaño del data nuevo: ", data.shape)
data.head()

data.drop(["Lat", "Long"], inplace=True, axis=1)
data.rename(columns={"Country/Region":"Bolivia"}, inplace=True)
data.head()

df_basura = data[data.Bolivia != "Bolivia"]
print(df_basura[0:30])
print(df_basura.shape)

paises_rep = data.Bolivia.duplicated().sum()
print("Países repetidos :", paises_rep)

data.drop_duplicates(subset=["Bolivia"], inplace=True)
paises_rep = data.Bolivia.duplicated().sum()
print("Países repetidos :", paises_rep)

data.set_index("Bolivia", inplace=True)
data.head()

fechas_rep = data.columns.duplicated().sum()
print("Fechas repetidas: ", fechas_rep)

for i in data.index:
  if i!="Bolivia":
    data.drop(i, inplace=True, axis=0)
    print(i)
data.head()

data.rename({"Bolivia":"Positivos"}, inplace=True, axis=0)
data.head()

"""####Cambiamos el dataset"""

copia = data.iloc[0]
copia.head()

df = pd.DataFrame(data=copia)
df.head()

df.reset_index(inplace=True)
df.head()

df.drop(range(0,150), inplace=True, axis=0)
df.rename(columns={"index":"FechaPositivos"}, inplace=True)
df.head()

df["FechaPositivos"] = pd.to_datetime(df["FechaPositivos"])
df.set_index("FechaPositivos", inplace=True)
df.head()

type(df.index)

"""####Visualizamos los datos"""

df["Positivos"].plot(figsize=(12,5))

casosReales = Image.open("DatosReales.jpg")
ax = plt.axes(xticks=[], yticks=[])
ax.imshow(casosReales)

"""####Verificamos estacionaridad"""

from statsmodels.tsa.stattools import adfuller

def ad_test(dataset):
  dftest = adfuller(dataset, autolag="AIC")
  print("1. ADF: ", dftest[0])
  print("2. P-Value: ", dftest[1])
  print("3. Num Lags: ", dftest[2])
  print("4. Num observaciones para regresión y valores críticos :", dftest[3])
  print("5. Valores críticos: ")
  for key, val in dftest[4].items():
    print("\t", key, ": ", val)

ad_test(df["Positivos"])

"""####Averiguamos el orden para el modelo"""

from pmdarima import auto_arima
#Ignorando las advertencias inofencivas
import warnings
warnings.filterwarnings("ignore")

stepwise_fit = auto_arima(df["Positivos"], trace= True, suppress_warnings=True)
stepwise_fit.summary()

"""####Importamos el modelo"""

from statsmodels.tsa.arima_model import ARIMA

"""####Hacemos Holdout"""

print("Sin holdout: ", df.shape)
train = df.iloc[:-14] #0.85
test = df.iloc[-14:] #0.85
print("Con holdout: ", train.shape, test.shape)

"""####Entrenamos el modelo"""

model = ARIMA(train["Positivos"], order=(2,2,3))
model = model.fit()
model.summary()

"""####Prediciendo en test"""

start = len(train)
end = len(train)+len(test)-1
y_pred = model.predict(start=start, end=end, typ="levels")
y_pred.index = df.index[start: end+1]
print(y_pred)
print("\n")
print(test)

"""####Visualizamos la predicción"""

y_pred.plot(legend=True)
test["Positivos"].plot(legend=True)

"""####Cálculo de error cuadrático aproximado"""

test["Positivos"].mean()

from sklearn.metrics import mean_squared_error
from math import sqrt
error_p = ((779*100)/1731)-30 #+70% contagioso
error_p = 100-error_p
print("Precisión: {:.2f}".format(error_p), "%")
rms = sqrt(mean_squared_error(y_pred, test["Positivos"]))
rms = rms + rms*(error_p/100)
print("Error medio: {:.2f}".format(rms))

"""####Aplicamos el modelo entrenado"""

model2 = ARIMA(df["Positivos"], order=(2,2,3))
model2 = model2.fit()
df.tail()

"""####Futuros positivos"""

index_future_dates = pd.date_range(start= '2021-01-29', end= '2021-02-28')
len(index_future_dates)

index_future_dates = pd.date_range(start= '2021-01-29', end= '2021-02-28')
#print(index_future_dates)
y_pred = model2.predict(start=len(df), end= len(df)+30, typ="levels").rename("Positivos")
y_pred.index= index_future_dates

aux = 0.00
for i in range(0,31):
  aux = y_pred[i]
  y_pred[i] = aux - rms
print(y_pred)

"""####Visualizamos la predicción"""

y_pred.plot(figsize=(12,5), legend=True)
plt.axhline(220000, c='r')
plt.axvline("2021-02-01", c='b')

plt.axhline(282000, c='r') #283500
plt.axvline("2021-02-27", c="g")

#print("Casos positivos para el '20 de Febrero': ", int(y_pred["2021-07-04"]))

primero_f = Image.open("1Febrero.jpg")
ax2 = plt.axes(xticks=[], yticks=[])
ax2.imshow(primero_f)

"""####Casos por departamento"""

T = 283922.527361
print("Casos 28 de Febrero del 2021")
print("SC = {:.2f}".format(T*0.3675))
print("LP = {:.2f}".format(T*0.2615))
print("CBBA = {:.2f}".format(T*0.09352))
print("CH = {:.2f}".format(T*0.0886))
print("OR = {:.2f}".format(T*0.0589))
print("TJ = {:.2f}".format(T*0.0424))
print("PT = {:.2f}".format(T*0.0402))
print("BN = {:.2f}".format(T*0.0383))
print("PN = {:.2f}".format(T*0.0064))

"""####Retroalimentamos para Marzo"""

copia2 = y_pred.iloc[0:30]
df2 = pd.DataFrame(data=copia2)
df2.reset_index(inplace=True)
df2.rename(columns={"index":"FechaPositivos"}, inplace=True)
df2["FechaPositivos"] = pd.to_datetime(df2["FechaPositivos"])
df2.set_index("FechaPositivos", inplace=True)
df2.head()

type(df2.index)

"""####Visualizamos los datos"""

df2["Positivos"].plot(figsize=(12,5))

"""####Verificamos la estacionaridad"""

def ad_test2(dataset):
  dftest2 = adfuller(dataset, autolag="AIC")
  print("1. ADF: ", dftest2[0])
  print("2. P-Value: ", dftest2[1])
  print("3. Num Lags: ", dftest2[2])
  print("4. Num observaciones para regresión y valores críticos :", dftest2[3])
  print("5. Valores críticos: ")
  for key, val in dftest2[4].items():
    print("\t", key, ": ", val)

ad_test2(df2["Positivos"])

stepwise_fit2 = auto_arima(df2["Positivos"], trace= True, suppress_warnings=True)
stepwise_fit2.summary()

print("Sin holdout: ", df2.shape)
train2 = df2.iloc[:-9] 
test2 = df2.iloc[-9:]
print("Con holdout: ", train2.shape, test2.shape)

"""####Entrenamos el modelo"""

model3 = ARIMA(train2["Positivos"], order=(0,1,1))
model3 = model3.fit()
model3.summary()

"""####Prediciendo en test"""

start2 = len(train2)
end2 = len(train2)+len(test2)-1
y_pred2 = model3.predict(start=start2, end=end2, typ="levels")
#y_pred2.index = df2.index[start: end2+1]
print(y_pred2)
print("\n")
print(test2)

"""####Visualizamos la predicción"""

y_pred2.plot(legend=True)
test2["Positivos"].plot(legend=True)

"""####Aplicamos el modelo entrenado"""

model3 = ARIMA(df2["Positivos"], order=(0,1,1))
model3 = model3.fit()
df2.tail()

"""####Cálculo del error cuadrático medio"""

test2["Positivos"].mean()

error_p2 = ((779*100)/1731)-40 #+60% (-10% por tasa de vacunación)
error_p2 = 100-error_p2
print("Precisión: {:.2f}".format(error_p2), "%")
rms2 = sqrt(mean_squared_error(y_pred2, test2["Positivos"]))
rms2 = rms2 + rms2*(error_p2/100)
print("Error medio: {:.2f}".format(rms2))

"""####Fechas futuras"""

index_future_dates2 = pd.date_range(start= '2021-02-27', end= '2021-03-29')
len(index_future_dates2)

index_future_dates2 = pd.date_range(start= '2021-02-27', end= '2021-03-29')
#print(index_future_dates)
y_pred2 = model3.predict(start=len(df2), end= len(df2)+30, typ="levels").rename("Positivos")
y_pred2.index= index_future_dates2

aux2 = 0.00
for i in range(0,31):
  aux2 = y_pred2[i]
  y_pred2[i] = aux2 - rms2
print(y_pred2)

"""####Visualizamos la predicción"""

y_pred2.plot(figsize=(12,5), legend=True)
plt.axhline(285000, c='r')
plt.axvline("2021-02-28", c='b')

plt.axhline(350563, c='r')
plt.axvline("2021-03-28", c="g")

