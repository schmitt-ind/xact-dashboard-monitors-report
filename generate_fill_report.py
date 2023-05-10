import http.client
import json
import csv

username = "your_username"
password = "your_password"

# get an access-token and client
connection = http.client.HTTPSConnection("api.dashboard.xact-data.com")
payload = json.dumps({"email": username,"password": password})
headers = {
    'Accept-Language': 'en',
    'Content-Type': 'application/json'
}
connection.request("POST", "/auth/login", payload, headers)
res = connection.getresponse()
data = res.read()
access_token = res.headers['access-token']
client = res.headers['client']

# get a list of tanks
payload = ''
headers = {
    'Accept-Lanuguage': 'en',
    'token-type': 'Bearer',
    'access-token': access_token,
    'client': client,
    'uid': username
}
connection.request("GET", "/tanks", payload, headers)
res = connection.getresponse()
data = res.read()
tanks = json.loads(data.decode("utf-8"))

# iterate through tanks list and compile tank info into a data list
data_list = []
for tank in tanks:
    if tank['tank_monitor']['status'] == 'active': # only report on active status tanks
        # create an object for the status of the alarms
        active_alarms = {'overfill': '', 'refill': '', 'critical': ''}
        for alarm in tank['alarms']:
            if alarm['name'] == 'overfill' and alarm['active']:
                active_alarms['overfill'] = 'Yes'
            if alarm['name'] == 'refill' and alarm['active']:
                active_alarms['refill'] = 'Yes'
            if alarm['name'] == 'critical' and alarm['active']:
                active_alarms['critical'] = 'Yes'
        row_list = [
            tank['tank_monitor']['esn'],
            tank['last_reading_at'],
            tank['description'],
            tank['current_level']['temp'],
            tank['zone']['name'],
            tank['current_level']['inventory_ratio'],
            tank['current_level']['inventory'],
            tank['current_level']['ullage'],
            tank['current_level']['battery_voltage'],
            tank['capacity'],
            tank['latitude'],
            tank['longitude'],
            active_alarms['refill'],
            active_alarms['critical'],
            active_alarms['overfill']
        ]
        data_list.append(row_list)

# Write tank info to csv file
header_list = [
    'ESN', 
    'Last measurement timestamp GMT', 
    'Location name', 
    'Temperature celcius', 
    'Zone name', 
    'Fill percent', 
    'Fill liters',
    'Ullage liters',
    'Battery voltage',
    'Capacity liters',
    'Latitude',
    'Longitude',
    'Refill alarm',
    'Critical alarm',
    'Overfill alarm'
    ]
with open('Tank_report.csv', 'w', newline='') as f: 
    write = csv.writer(f)
    write.writerow(header_list)
    write.writerows(data_list)
