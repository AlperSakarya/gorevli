# gorevli
Small operational web application for nonprofits using Python and Flask.
 
The project is intended to be browsed from mobile devices, and can be displayed in full-screen browsing mode in internet browsers e.g F11 in Chrome.


<b>Features:</b><br>
- One time or recurring donations and payment receipts via Stripe
- Registered Members are kept in Square (will be moved to a local DB soon)
- Ability to send SMS to all registered users from the admin panel via twilio

<b>Setup:</b><br>
- The app will check for the local DB and re-create if does not exist on every run. It does not write an existing DB.
Just run the routes.py file and install the requirements.
Requirements are still not %100 listed but you can figure out from the import list.

<b>Language:</b><br>
- The project is in Turkish, but it's not hard to just replace simple sentences. They are either success or error messages under page names that are in English.
If you like and need me to translate it for you, open an issue with your contact details.