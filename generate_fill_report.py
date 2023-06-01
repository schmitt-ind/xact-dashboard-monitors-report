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

# get a list of monitors
payload = ''
headers = {
    'Accept-Lanuguage': 'en',
    'token-type': 'Bearer',
    'access-token': access_token,
    'client': client,
    'uid': username
}
connection.request("GET", "/monitors", payload, headers)
res = connection.getresponse()
data = res.read()
monitors = json.loads(data.decode("utf-8"))

# iterate through monitors list and compile monitor info into a data list
data_list = []
for monitor in monitors:
    if monitor['status'] == 'active': # only report on active status monitors
        # create an object for the status of the alarms
        active_alarms = {'overfill': '', 'refill': '', 'critical': ''}
        for alarm in monitor['alarms']:
            if alarm['name'] == 'overfill' and alarm['active']:
                active_alarms['overfill'] = 'Yes'
            if alarm['name'] == 'refill' and alarm['active']:
                active_alarms['refill'] = 'Yes'
            if alarm['name'] == 'critical' and alarm['active']:
                active_alarms['critical'] = 'Yes'
        row_list = [
            monitor['esn'],
            monitor['last_reading_at'],
            monitor['description'],
            monitor['current_level']['temp'],
            monitor['zone']['name'],
            monitor['current_level']['inventory_ratio'],
            monitor['current_level']['inventory'],
            monitor['current_level']['ullage'],
            monitor['current_level']['battery_voltage'],
            monitor['capacity'],
            monitor['latitude'],
            monitor['longitude'],
            active_alarms['refill'],
            active_alarms['critical'],
            active_alarms['overfill']
        ]
        data_list.append(row_list)

# Write monitor info to csv file
header_list = [
    'ESN', 
    'Last measurement timestamp GMT', 
    'Location name', 
    'Temperature celsius', 
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
with open('monitor_report.csv', 'w', newline='') as f: 
    write = csv.writer(f)
    write.writerow(header_list)
    write.writerows(data_list)
