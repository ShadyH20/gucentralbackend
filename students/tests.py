from django.test import TestCase
from scrapper import Scrapper

# Create your tests here.
username = 'shady.farag'
password = 'Do2zhe@14'














































scrapper = Scrapper(username=username, password=password)
scrapper.get_year_transcript("2022-2023")
# print(scrapper.get_courses_data())