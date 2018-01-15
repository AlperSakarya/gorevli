# gorevli
A lite, operational web application for nonprofits using Python, Flask, Stripe and Twilio.
 
The project is intended to be browsed from mobile devices, and can be displayed in full-screen browsing mode in internet browsers e.g F11 in Chrome.


<b>Features:</b><br>
- One time or recurring monthly CC donations and payment receipts via Stripe
- Registered Members are kept in a local SQLite DB with their Stripe Customer ID, email and phone number
- Seperate Newsletter Signup for SMS messaging, ability to send SMS to all registered users from the admin panel via Twilio

<b>Setup:</b><br>
- The app will check for the local DB and re-create if does not exist on every run. It does not write an existing DB.
- Just run the routes.py file and install the requirements.
Requirements are still not %100 listed but you can figure out from the import list.
- you need to create an auth.py in the same directory and provide all the API credentials for Stripe, Twilio and admin panel in there.

<b>Misc:</b><br>
- Newsletter and donation customers are kept in same table. If found same email, users get merged and columns get updated with missing informaiton.
- I've dropped using Square as it does not have recurring payments via API. I was only using it to store users to not maintain a DB but I had to move it to SQLite to store Stripe customer IDs with email address.
- If you need Square usage examples check the earlier commits

<b>Language:</b><br>
- The project is in Turkish, but it's not hard to just replace simple sentences. They are either success or error messages under page names that are in English.
If you like and need me to translate it for you, open an issue with your contact details.
