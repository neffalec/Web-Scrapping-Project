""" 
CS313E: Term Project

Author: Alec Neff

UTEID: aen828

Date Last Modified: 11/26/2023
"""

import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np

def scrape_weather_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    weather_forecast = []
    #find the main container for the weather timeline using inspect
    main_container = soup.find('div', class_='weather-timeline__timeline weather-timeline__timeline--seven-day')
    #iterate over through each timeline item
    for item in main_container.find_all('div', class_='weather-timeline__timeline-item'):
        day = item.find('h4', class_='day').text.strip()  #get the day from the webpage
        high_temp = item.find('span', class_='high').text.strip()  # find the high temperature
        low_temp = item.find('span', class_='low').text.strip()  #find the low temperature
        weather_forecast.append((day, high_temp, low_temp))
    return weather_forecast

def process_data(weather_data):
    #weather_data is a list of tuples (day, high_temp, low_temp)
    processed_data = {'Day': [], 'High Temp': [], 'Low Temp': []}
    for day, high, low in weather_data:
        processed_data['Day'].append(day)
        #we needed to replace the degree sign 
        processed_data['High Temp'].append(int(high.replace('°', '')))
        processed_data['Low Temp'].append(int(low.replace('°', '')))
    return processed_data

def visualize_data(processed_data, days_for_jacket):
    days = processed_data['Day']
    high_temps = processed_data['High Temp']
    low_temps = processed_data['Low Temp']
    day_indices = np.arange(len(days))
    #find the midpoints between high and low temp
    mid_temps = (np.array(high_temps) + np.array(low_temps)) / 2
    
    #multiple subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8))
    #Subplot 1: Line plot for high and low temperatures
    ax1.plot(day_indices, high_temps, label='High Temp', color='red')
    ax1.plot(day_indices, low_temps, label='Low Temp', color='blue')
    for i, (day, high, low) in enumerate(zip(days, high_temps, low_temps)):
        if day in days_for_jacket:
            ax1.scatter([i], [high], color='green', marker='*', s=100)
            ax1.scatter([i], [low], color='green', marker='*', s=100)
    ax1.set_xticks(day_indices)
    ax1.set_xticklabels(days)
    ax1.set_xlabel('Day of the Week')
    ax1.set_ylabel('Temperature (°F)')
    ax1.set_title('7-Day Weather Forecast')
    ax1.legend()

    #Subplot 2: Bar-like plot connecting high and low temps
    ax2.errorbar(day_indices, mid_temps, 
                 yerr=[mid_temps - np.array(low_temps), np.array(high_temps) - mid_temps], 
                 fmt='o', color='blue', ecolor='gray', elinewidth=3, capsize=0)
    ax2.set_xticks(day_indices)
    ax2.set_xticklabels(days)
    ax2.set_xlabel('Day of the Week')
    ax2.set_ylabel('Temperature Range (°F)')
    ax2.set_title('Temperature Range for Each Day')
    plt.tight_layout()
    plt.show()
    
def find_days_for_jacket(processed_data):
    days_for_jacket = []
    for day, high, low in zip(processed_data['Day'], processed_data['High Temp'], processed_data['Low Temp']):
        if high - low > 18:
            days_for_jacket.append(day)
    return days_for_jacket

def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid][1] == target:
            return arr[mid]
        elif arr[mid][1] < target:
            low = mid + 1
        else:
            high = mid - 1
    return None

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2][1]
    left = [x for x in arr if x[1] < pivot]
    middle = [x for x in arr if x[1] == pivot]
    right = [x for x in arr if x[1] > pivot]
    return quicksort(left) + middle + quicksort(right)

def main():
    url = 'https://www.kxan.com/weather/'
    raw_data = scrape_weather_data(url)
    processed_data = process_data(raw_data)
    #sort the data by high temperature for a binary search
    sorted_by_high_temp = quicksort([(day, high) for day, high in zip(processed_data['Day'], processed_data['High Temp'])])
    #use a binary search for a specific high temperature
    target_temperature = 75  #Harmful temperatures
    result = binary_search(sorted_by_high_temp, target_temperature)
    if result:
        print(f"Found day with target high temperature {target_temperature} degrees: {result[0]}")
    else:
        print(f"No day found with high temperature of {target_temperature} degrees")
    jacket_days = find_days_for_jacket(processed_data)
    if jacket_days:
        print('Consider bringing a jacket or change of clothes on these days this week:', jacket_days)
        print('Days are represented with asterisks on the graph provided.')
    else:
        print('No large temperature differences expected this week!')
    visualize_data(processed_data, jacket_days)

if __name__ == "__main__":
    main()



