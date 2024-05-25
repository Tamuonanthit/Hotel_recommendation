import re
import traceback
import pandas as pd
import sqlite3
import ast
from ast import literal_eval
from Content_based import ContentRecommender
from Filter_based import FilterRecommender 

class CombineRecommender:
    def __init__(self, database):
        self.ct = ContentRecommender(database)
        self.fr = FilterRecommender(database)

    def recommend(self, city, roomtype, amenities, min_price, max_price, days):
        filtered_hotels = self.get_filtered_data(city, roomtype, amenities, min_price, max_price, days)
        
        if filtered_hotels.empty:
            print('No hotels available after filtering')
            return pd.DataFrame()

        listing_ids = filtered_hotels['listing_id'].tolist()
        similar_hotels = self.ct.recommend_by_amenities_topic(listing_ids)
        similiar_hotels= similar_hotels.drop_duplicates(subset='listing_id',keep='first')
        sorted_hotel= similiar_hotels.sort_values(by='review_scores_rating', ascending=False)
        return sorted_hotel
    
    def get_filtered_data(self, city, roomtype, amenities, min_price, max_price, days):
        filtered_hotels = self.fr.filter_by_all(city, roomtype, amenities, min_price, max_price, days)
        return filtered_hotels

    

