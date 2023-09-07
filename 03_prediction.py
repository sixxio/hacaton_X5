import tensorflow as tf
import keras as keras
import numpy as np
import pandas as pd
import pickle #для сохранения и загрузки tokenizer'а

from keras import utils #утилита для работы с нейронными сетями
from keras.preprocessing.text import Tokenizer #для преобразования текстовых данных в числовые тензоры

from keras.models import Sequential # для создания архитектур нейронных сетей
from keras.models import load_model # для загрузки архитектур и весов нейронных сетей

# 
id_address = pd.read_excel('database\shops_rates.xlsx', usecols=['id', 'address'])
shop_reviews = pd.read_excel('input\shop_reviews.xlsx')

def prediction_list(id_address, shop_reviews):

    # # # Загружаеем файлы tokenizer'а и обучающую базу
    # with open('input/tokenizer.pickle', 'rb') as handle:
    #     tokenizer = pickle.load(handle)

    # model = load_model('input/model.h5') # Размер будет порядка 50Mb, возможно побольше...

    shop_id = shop_reviews.id[0] #Берём id магазина
    shop_address = id_address.address[id_address.index[id_address.id == shop_id][0]] #Берём адрес по id

    prediction = [] #Собираем отчёт для демонстрации
    prediction.append([shop_id, shop_address])
    for i in range(len(shop_reviews)):
        prediction.append([shop_reviews.text[i], shop_reviews.rate[i]])

    return prediction