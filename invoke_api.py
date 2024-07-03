import requests

url = "http://127.0.0.1:5000/flight"
# params = {
#     "carrierCode": "CX",
#     "flightNumber": "888",
#     "scheduledDepartureDate": "2024-06-28"
# }

# params = {'departure': 'HKG',
#           'arrival': 'YVR',
#           'date_from': '2024-05-31',
#           'date_to': '2024-05-31',
#           'airline': 'CX',
#           'flight_num': '888'
#           }

params = {'departure': 'DEL',
          'arrival': 'HKG',
          'date_from': '2024-05-30',
          'date_to': '2024-05-30',
          'airline': 'CX',
          'flight_num': '698'
          }

response = requests.get(url, params=params)

# check the response status code
if response.status_code == 200:
    print(response.text)
else:
    print(f"Request failed with status code: {response.status_code}")