import requests
from datetime import datetime, timedelta

# token = "qkEWInAtFs38T6pbUPFDzk67qrM9"

def get_flight_info(flight_info):
    url = f"https://aviation-edge.com/v2/public/flightsHistory"

    # headers = {
    #     "Authorization": f"Bearer {token}",
    #     "Content-Type": "application/json"
    # }

    date_str = flight_info['date_from']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    new_date_obj = date_obj - timedelta(days=1)
    new_date_str = new_date_obj.strftime('%Y-%m-%d')
    # print(new_date_str)
    
    params = {
        "key":'b6fce0-7f302f',
        "code": flight_info['code'],
        "type": flight_info['type'],
        "date_from": new_date_str,
        "date_to": flight_info['date_to'],
        "airline_iata": flight_info['airline_iata'],
        "flight_num": flight_info['flight_num']
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(response.text)
        return 

    data = response.json()

    delay_info = {}

    for flight in data:
        if flight[flight_info['type']]["iataCode"] == flight_info['code'].lower() and \
        flight["departure"]["scheduledTime"][0:10] == flight_info['date_from'] and \
        flight["airline"]["iataCode"] == flight_info['airline_iata'].lower() and \
        flight["flight"]["number"] == flight_info['flight_num']:
            delay_info ={
                'departure': flight["departure"]["iataCode"],
                'arrival': flight["arrival"]["iataCode"],
                'delay': flight["departure"]["delay"],
                "scheduledTime": flight["departure"]["scheduledTime"],
                "actualTime": flight["departure"]["actualTime"]
            }
    
    # print(delay_info)
    return delay_info

    
# flight = {'code': 'YVR',
#           'type': 'arrival',
#           'date_from': '2024-05-31',
#           'date_to': '2024-05-31',
#           'airline_iata': 'CX',
#           'flight_num': '7013'
#           }
# get_flight_info(flight)