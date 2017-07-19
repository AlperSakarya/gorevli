from __future__ import print_function

import squareconnect
from squareconnect.apis.customers_api import CustomersApi
from squareconnect.rest import ApiException
import auth

api_instance = CustomersApi()

try:
    # list customers
    api_response = api_instance.list_customers()
    #print (api_response.customers)
    for i in api_response.customers:
        print ("Email Address: ")
        print(i.email_address)
        print("Phone Number: ")
        print(i.phone_number)
        #print(api_response.customers[0])



    #print (api_response.customers)

except ApiException as e:
    print ('Exception when calling CustomersApi->list_customers: %s\n' % e)


