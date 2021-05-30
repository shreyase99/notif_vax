# notif_vax
Notifies user with a push notification when vaccine slots are available.

Also records vaccine availability datapoints in a JSON dump

### Instructions:
1. Create a Pushover account (https://pushover.net/). It has a 1 month free trial.
2. Register a new application in Pushover and note the User Token and the Application Token.
3. Set the tokens as environment variables PUSHOVER_USER AND PUSHOVER_TOKEN (in .bashrc for linux)
4. Download Pushover App on phone, login with same credentials. 
5. Set suitable ringtones, enable autostart, disbale power save, and lockscreen notifications.
6. Install the dependencies from requirements.txt
7. Find state ID (from https://cdn-api.co-vin.in/api/v2/admin/location/states) and then district ID (from https://cdn-api.co-vin.in/api/v2/admin/location/districts/ **stateID**). 
8. Modify the global variables in the script (Age, District/Pincode, Dose, Logging)
9. Alternatively, PINCODE can be used instead of District ID. Uncomment the 'url' variable declaration suitably.
7. Start the notif_vax.py script in a detached terminal (screen).  
