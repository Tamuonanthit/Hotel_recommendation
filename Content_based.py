import re
import traceback
import numpy as np
import pandas as pd

import math
import os
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

import sqlite3
from collections import Counter
import ast
from ast import literal_eval

class ContentRecommender:
    def __init__(self, database):
        self.database = database
        pass

    def query(self, sql):
        try:
            conn = sqlite3.connect(self.database)
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            return df
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def get_data_hotel(self):
        hotel_details = self.query('select * from airbnb_data')
        df_hotel_details = pd.DataFrame(hotel_details)
        # Xử lý dữ liệu
        df_hotel_details.dropna()
        df_hotel_details.drop_duplicates(subset='listing_id', keep=False, inplace=True)
        data_hotel = pd.DataFrame(df_hotel_details)
        return data_hotel

    def recommend_by_amenities_topic(self):
        data = self.get_data_hotel()
        data['amenities'] = data['amenities'].apply(ast.literal_eval)
        data['Topics'] = data['Topics'].apply(ast.literal_eval)
        data['combined_features'] = (data['amenities']).apply(lambda x: ' '.join(x))
        vect = CountVectorizer()
        tfidf = TfidfVectorizer()
        vect_matrix = vect.fit_transform(data['combined_features'])
        tfidf_matrix = tfidf.fit_transform(data['combined_features'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        businesses = data['listing_id']
        indices = pd.Series(businesses.index, index=data['listing_id'])

        def content_recommendations(business):
            idx = indices[business]
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:21]
            biz_indices = [i[0] for i in sim_scores]
            return data.iloc[biz_indices]

        return content_recommendations

    def recommend(self, city, roomtype, min_price, max_price, days):
        data = self.get_data_hotel()
        data['room_type'] = data['room_type'].str.lower()
        data['city'] = data['city'].str.lower()
        data['price'] = data['price'].replace('[\$,]', '', regex=True)
        data['price'] = pd.to_numeric(data['price'], errors='coerce')
        data['minimum_nights'] = pd.to_numeric(data['minimum_nights'], errors='coerce')

        # Filter data based on input parameters
        filtered_data = data[(data['city'] == city.lower()) &
                             (data['room_type'] == roomtype.lower()) &
                             (data['price'] >= min_price) &
                             (data['price'] <= max_price) &
                             (data['minimum_nights'] >= days)]

        if not filtered_data.empty:
            return self.recommend_by_amenities_topic()(filtered_data.iloc[0]['listing_id'])
        else:
            print('No hotels available with specified criteria')
            return pd.DataFrame()
