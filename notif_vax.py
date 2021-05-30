from datetime import date as dt, timedelta
import requests
import sys
import os
import smtplib
import http.client, urllib
import time as tm
import json

# Get District ID from CoWin API website
DISTRICT_ID=581
#Pincode covers a smaller geography
PINCODE = 500038	
# 0 for Both Doses, 1 for Dose 1, 2 for Dose 2
DOSE = 2
# Age
AGE = 48
# Toggle Logging
JSON_LOGGING = True

def push_notif(msg):
	user_key = os.environ["PUSHOVER_USER"]
	pushover_token = os.environ["PUSHOVER_TOKEN"]
	conn = http.client.HTTPSConnection("api.pushover.net:443")
	conn.request("POST", "/1/messages.json",
		urllib.parse.urlencode({
	    "token": pushover_token,
	    "user": user_key,
	    "message": msg,
		}), { "Content-type": "application/x-www-form-urlencoded" 
		})
	conn.getresponse()

def get_slots_for_week(d):
	print("Checking for week - " + d + " 6 Days...")
	#url="https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + str(PINCODE)+ "&date=" + d
	url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=" + str(DISTRICT_ID) + "&date=" + d
	response = requests.get(url, headers = {
		'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36'
	})

	available_slots = []
	if response.status_code == 200:
		json_response = response.json()
		for center in json_response["centers"]:
			for session in center["sessions"]:
				if session["min_age_limit"] > AGE:
					continue
				if session["available_capacity"] == 0:
					continue
				if DOSE == 1 and session["available_capacity_dose1"] == 0:
					continue
				if DOSE == 2 and session["available_capacity_dose2"] == 0:
					continue
				new_sess = session
				new_sess["center_id"] = center["center_id"]
				new_sess["name"] = center["name"]
				new_sess["address"] = center["address"]
				available_slots.append(new_sess)
		if len(available_slots) > 0:
			print("Slots found")
			return available_slots
			
		else:
			print("No slots found")
	else:
		print(response.text)
	return None

def call_per_week():
	SLEEP_TIME = 4
	INIT_COUNT = -12
	RESET_COUNT = 48

	count = INIT_COUNT
	push_calls = 0
	total_lines_json = 0
	while True:
		# Frequency to limit 100 API calls per 5 Min
		if count == -12:
			print("Cold Time")
		else:
			print("Hot Time, count = " + str(count))
		date = dt.today().strftime("%d-%m-%Y")
		available_slots = get_slots_for_week(date)
		current_time = tm.ctime()
		if available_slots != None:
			msg = ""
			for i, slot in enumerate(available_slots):
				num = 0
				if DOSE == 0:
					num = slot["available_capacity"]
				if DOSE == 1:
					num = slot["available_capacity_dose1"]
				if DOSE == 2:
					num = slot["available_capacity_dose2"]
				msg = msg + "[" + slot["name"] + ", " + slot["vaccine"] + ", " + str(num) + "]"
				if i < len(available_slots)-1:
					msg = msg + ", " 
				slot["observed"] = current_time
				slot["dose"] = DOSE
			if JSON_LOGGING==True:
				fname = "Vaccine-Dump-" + date
				with open(fname, 'a') as file:
				    for slot in available_slots:
				        json.dump(slot, file)
				        file.write('\n')
				        total_lines_json += 1
			if count < 0 and count % 4 == 0:
				print("Notifying...")
				push_notif(msg)
				push_calls += 1
			count += 1
			if count == RESET_COUNT:
				count = INIT_COUNT	
			if total_lines_json >= 1000000:
				break
			if push_calls >= 300:
				break
		else:
			count = INIT_COUNT
		print("")
		tm.sleep(SLEEP_TIME)

if __name__ == "__main__":
	call_per_week()
	
	
