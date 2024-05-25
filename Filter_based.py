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


class FilterRecommender:
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

    def city_based(self, city):
        data_hotel = self.get_data_hotel()
        data_hotel['city'] = data_hotel['city'].str.lower()
        # Lọc dữ liệu theo thành phố
        citybased = data_hotel[data_hotel['city'] == city.lower()]
        citybased = citybased.sort_values(by='review_scores_rating', ascending=False)
        # Loại bỏ các bản ghi trùng lặp
        citybased.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        if not citybased.empty:
            hname = citybased[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url']]
            return hname.head()
        else:
            print('No hotels available')

    def roomtype_based(self, roomtype):
        data_hotel = self.get_data_hotel()
        data_hotel['room_type'] = data_hotel['room_type'].str.lower()
        roomtypebased = data_hotel[data_hotel['room_type'] == roomtype.lower()]
        roomtypebased = roomtypebased.sort_values(by='review_scores_rating', ascending=False)
        roomtypebased.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        if not roomtypebased.empty:
            hname = roomtypebased[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url']]
            return hname.head()
        else:
            print('No hotels available')
            return pd.DataFrame()

    def pop_citybased(self, city, roomtype):
        data_hotel = self.get_data_hotel()

        data_hotel['city'] = data_hotel['city'].str.lower()
        data_hotel['room_type'] = data_hotel['room_type'].str.lower()

        popbased = data_hotel[data_hotel['city'] == city.lower()]
        popbased = popbased[popbased['room_type'] == roomtype.lower()].sort_values(by='review_scores_rating',
                                                                                   ascending=False)

        popbased.drop_duplicates(subset='listing_id', keep='first', inplace=True)
        if not popbased.empty:
            hname = popbased[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url']]
            return hname.head()
        else:
            print('No hotels available')
            return pd.DataFrame()

    def get_all_amenities(self):
        df_amenities = self.query('select amenities from airbnb_data')
        df_amenities['amenities'] = df_amenities['amenities'].apply(ast.literal_eval)
        result_amenities = pd.DataFrame(df_amenities)
        return result_amenities

    def amenities_based(self, amenities):
        data_hotel = self.get_data_hotel()
        has_amenities = data_hotel[data_hotel['amenities'].apply(lambda x: set(amenities).issubset(x))]

        if not has_amenities.empty:
            # Return the hotels that have all specified amenities
            return has_amenities[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url']]
        else:
            # If no hotels have all specified amenities, print a message and return an empty DataFrame
            print('No hotels available with specified amenities')
            return pd.DataFrame()

    def price_range_based(self, min_price, max_price):
        # Ensure min_price is less than or equal to max_price
        if min_price > max_price:
            print('Error: min_price should be less than or equal to max_price')
            return pd.DataFrame()

        # Get hotel data
        data_hotel = self.get_data_hotel()
        # Remove '$' and convert 'price' column to numeric
        data_hotel['price'] = data_hotel['price'].replace('[\$,]', '', regex=True)
        data_hotel['price'] = pd.to_numeric(data_hotel['price'], errors='coerce')

        # Filter hotels within the price range
        price_filtered_hotels = data_hotel[(data_hotel['price'] >= min_price) & (data_hotel['price'] <= max_price)]
        # Sort filtered hotels by price
        price_filtered_hotels_sorted = price_filtered_hotels.sort_values(by='review_scores_rating')
        # Remove duplicates based on 'listing_id'
        price_filtered_hotels_sorted.drop_duplicates(subset='listing_id', keep='first', inplace=True)

        # Select relevant columns to return
        if not price_filtered_hotels_sorted.empty:
            hname = price_filtered_hotels_sorted[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url', 'price']]
            return hname
        else:
            print('No hotels available')
            return pd.DataFrame()

    def days_based(self, days):
        # Get hotel data
        data_hotel = self.get_data_hotel()
        data_hotel['minimum_nights'] = pd.to_numeric(data_hotel['minimum_nights'], errors='coerce')
        days_filtered_hotels = data_hotel[data_hotel['minimum_nights'] >= days]

        # Sort filtered hotels by price
        days_filtered_hotels_sorted = days_filtered_hotels.sort_values(by='review_scores_rating', ascending=False)
        # Remove duplicates based on 'listing_id'
        days_filtered_hotels_sorted.drop_duplicates(subset='listing_id', keep='first', inplace=True)

        # Select relevant columns to return
        if not days_filtered_hotels_sorted.empty:
            hname = days_filtered_hotels_sorted[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url', 'price']]
            return hname
        else:
            print('No hotels available')
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

    def distance_based(self, city, max_distance):
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
        nearby_hotels_sorted = nearby_hotels.sort_values(by='distance')
        if not nearby_hotels_sorted.empty:
            hname = nearby_hotels_sorted[
                ['name', 'review_scores_rating', 'room_type', 'amenities', 'minimum_nights', 'listing_url', 'price',
                 'distance']]
            return hname.head()
        else:
            print('No hotels available')
            return pd.DataFrame()



