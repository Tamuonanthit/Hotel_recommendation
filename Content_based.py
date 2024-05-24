import re
import traceback
import numpy as np
import pandas as pd
import math
import os
import sqlite3
from collections import Counter
from ast import literal_eval
import ast

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
        df_hotel_details.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        data_hotel = pd.DataFrame(df_hotel_details)
        return data_hotel

    def city_based(self, city):
        data_hotel = self.get_data_hotel()
        data_hotel['city'] = data_hotel['city'].str.lower()
        # Lọc dữ liệu theo thành phố
        citybased = data_hotel[data_hotel['city'] == city.lower()]
        citybased = citybased.sort_values(by='review_scores_rating', ascending=False)
        # Loại bỏ các bản ghi trùng lặp
        citybased.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        if not citybased.empty:
            hname = citybased[['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url']]
            return hname
        else:
            print('No hotels available')

    def roomtype_based(self, roomtype):
        data_hotel = self.get_data_hotel()
        data_hotel['room_type'] = data_hotel['room_type'].str.lower()
        roomtypebased = data_hotel[data_hotel['room_type'] == roomtype.lower()]
        roomtypebased = roomtypebased.sort_values(by='review_scores_rating', ascending=False)
        roomtypebased.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        if not roomtypebased.empty:
            hname = roomtypebased[['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url']]
            return hname
        else:
            print('No hotels available')

    def pop_citybased(self, city, roomtype):
        data_hotel = self.get_data_hotel()

        data_hotel['city'] = data_hotel['city'].str.lower()
        data_hotel['room_type'] = data_hotel['room_type'].str.lower()

        popbased = data_hotel[data_hotel['city'] == city.lower()]
        popbased = popbased[popbased['room_type'] == roomtype.lower()].sort_values(by='review_scores_rating',
                                                                                   ascending=False)

        popbased.drop_duplicates(subset='id', keep='first', inplace=True)
        if not popbased.empty:
            hname = popbased[['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url']]
            return hname
        else:
            print('No hotels available')

    def get_all_amenities(self):
        df_amenities = self.query('select amenities from airbnb_data')
        # Áp dụng hàm literal_eval
        df_amenities['amenities'] = df_amenities['amenities'].apply(ast.literal_eval)
        result_amenities = pd.DataFrame(df_amenities)
        return result_amenities

    def recommend_by_amenities(self, amenities):
        data_hotel = self.get_all_amenities()

        # Check if each hotel contains all specified amenities
        has_amenities = data_hotel[data_hotel['amenities'].apply(lambda x: set(amenities).issubset(x))]

        if not has_amenities.empty:
            # Return the hotels that have all specified amenities
            return has_amenities[['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url']]
        else:
            # If no hotels have all specified amenities, print a message and return an empty DataFrame
            print('No hotels available with specified amenities')
            return pd.DataFrame()


    def distance(self, coord1, coord2):
        R = 6373.0  # Radius of Earth in kilometers
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        lat1, lon1 = np.radians(lat1), np.radians(lon1)
        lat2, lon2 = np.radians(lat2), np.radians(lon2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        dist = R * c / 1.6
        return dist

    def recommend_nearby_hotels(self, city, max_distance):
        city_coords = {
            'New Jersey': (40.0583, -74.4057),
            'Washington DC': (38.9072, -77.0369),
            'Seattle': (47.6062, -122.3321),
            'Chicago': (41.8781, -87.6298),
            'Texas': (31.9686, -99.9018),
            'Boston': (42.3601, -71.0589),
            'San Diego': (32.7157, -117.1611),
            'Dallas': (32.7767, -96.7970)
        }

        if city not in city_coords:
            print(f"Coordinates for {city} not found.")
            return pd.DataFrame()

        target_coord = city_coords[city]
        data_hotel = self.get_data_hotel()

        # Convert latitude and longitude to numeric values, forcing errors to NaN
        data_hotel['latitude'] = pd.to_numeric(data_hotel['latitude'], errors='coerce')
        data_hotel['longitude'] = pd.to_numeric(data_hotel['longitude'], errors='coerce')

        # Drop rows with missing latitude or longitude
        data_hotel.dropna(subset=['latitude', 'longitude'], inplace=True)

        # Calculate the distance of each hotel to the target city coordinates
        data_hotel['distance'] = data_hotel.apply(
            lambda row: self.distance(target_coord, (row['latitude'], row['longitude'])),
            axis=1
        )

        # Filter hotels by the specified city and distance
        data_hotel_with_distances = data_hotel[data_hotel['city'].str.lower() == city.lower()]
        nearby_hotels = data_hotel_with_distances[data_hotel_with_distances['distance'] <= max_distance]

        return nearby_hotels.sort_values(by='distance')

    def recommend_hotels_by_price_range(self, min_price, max_price):
        # Ensure min_price is less than or equal to max_price
        if min_price > max_price:
            print('Error: min_price should be less than or equal to max_price')
            return pd.DataFrame()

        # Get hotel data
        data_hotel = self.get_data_hotel()
        # Remove '$' and convert 'price' column to numeric
        data_hotel['price'] = data_hotel['price'].replace('[\$,]', '', regex=True)
        data_hotel['price'] = pd.to_numeric(data_hotel['price'], errors='coerce')
        print("Data after removing '$':")
        print(data_hotel['price'])

        # Filter hotels within the price range
        price_filtered_hotels = data_hotel[(data_hotel['price'] >= min_price) & (data_hotel['price'] <= max_price)]
        print("Hotels within the price range:")
        print(price_filtered_hotels)

        # Sort filtered hotels by price
        price_filtered_hotels_sorted = price_filtered_hotels.sort_values(by='price')

        # Remove duplicates based on 'listing_id'
        price_filtered_hotels_sorted.drop_duplicates(subset='listing_id', keep='first', inplace=True)

        # Select relevant columns to return
        if not price_filtered_hotels_sorted.empty:
            hname = price_filtered_hotels_sorted[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url', 'price']]
            return hname
        else:
            print('No hotels available')
            return pd.DataFrame()

    def calculate_similarity(self, row, city, roomtype, min_price, max_price):
        score = 0

        if row['city'].lower() == city.lower():
            score += 1

        if row['room_type'].lower() == roomtype.lower():
            score += 1


        if min_price <= row['price'] <= max_price:
            score += 1

        return score

    def recommender(self, city, room_type,  price_from, price_to):
        data_hotel = self.get_data_hotel()

        # Convert 'price' column to numeric
        data_hotel['price'] = data_hotel['price'].replace('[\$,]', '', regex=True)
        data_hotel['price'] = pd.to_numeric(data_hotel['price'], errors='coerce')

        data_hotel['similarity'] = data_hotel.apply(
            lambda row: self.calculate_similarity(row, city, room_type, price_from, price_to), axis=1
        )
        recommendations = data_hotel.sort_values(by='similarity', ascending=False)
        if not recommendations.empty:
            return recommendations[['name', 'review_scores_rating', 'room_type', 'amenities', 'listing_url', 'price', 'similarity']]
        else:
            print('No hotels available')
            return pd.DataFrame()



#### TEST
database='airbnb_data.db'
ct = ContentRecommender(database)

result=ct.get_data_hotel()
print(result['price'])

result2=ct.city_based('Washington DC')
print(result2)

result3=ct.roomtype_based('private room')
print(result3)


result4=ct.recommend_nearby_hotels('Washington DC',10)
print(result4)

result5=ct.recommend_hotels_by_price_range(20,50)
print(result5)

result6=ct.get_all_amenities()
print(result6)

result7=ct.recommend_by_amenities('microwave')
print(result7)

result8=ct.recommender('Washington DC','private room' , 20, 50)
print(result8)