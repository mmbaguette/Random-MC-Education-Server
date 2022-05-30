import requests
import itertools
import os
import json
import threading
import traceback
import time

'''
Written by mmbaguette on GitHub

This program uses the Minecaft Education Edition undocumented API to find random servers.
This goes through every single possible code combination.

Takes over 12 hours!

--UPDATE--
I'll be using multi-threading to speed up the process a TON.
Can we find all codes in under 5 hours?

--RESULT--
its like super fast... all codes in 2 hours or less

--UPDATE--
Multi-processing???

--RESULT--
too complex not worth it

--UPDATE--
instead of setting the number of threads to os.cpucount, just set to a big number! 
(45 threads, 58 requests a second!) however, sometimes it doesn't work that fast

--UPDATE-- Oct 3 2021
MOST codes found after ~25000 - ~29000 and end at ~37000 -- Might start and end there?

--RESULT--
Wrong, maybe just a coincidence that all the codes were there at that time. 
Only found a single code.
'''

icon_names = [
    "Book & Quill",
    "Balloon",
    "Rail",
    "Alex",
    "Cookie",
    "Fish",
    "Agent",
    "Cake",
    "Picaxe",
    "Water Bucket",
    "Steve",
    "Apple",
    "Carrot",
    "Panda",
    "Sign",
    "Potion",
    "Map",
    "Llama"
]

joinInfodata = {
  "build": 11731000,
  "locale": "en_US",
  "protocolVersion": 1,
}

user_headers = {
    "User-Agent": "cpprestsdk/2.10.2"
}

codes_searched = [] # all list of codes searched from each thread
codes_data = {} # "externalIp": {"serverName":"e.t.c."}
jwt_expired = False

def write_codes():
    # write down the codes we saved
    f = open(os.getcwd() + "\\codes.json","w")
    f.write(json.dumps(codes_data, indent=4))
    f.close()

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def make_request(joinInfUurl, headers):
    try:
        r = requests.post(url=joinInfUurl, json=joinInfodata,headers=headers, timeout=3)
        return r
    except ValueError:
        traceback.print_exc()
        print("\nWaiting for you to PAUSE Fiddler capturing (or something else went wrong)!")
        return
    except (requests.ConnectTimeout, requests.exceptions.ReadTimeout):
        print("Request timed out.")
        make_request(joinInfUurl, headers)
    except:
        print("Something else went wrong. Retrying:")
        traceback.print_exc()
        make_request(joinInfUurl, headers)

def get_pass_names(passcode: str) -> str:
    return ", ".join([icon_names[int(x)] for x in passcode.split(",")])

def find_codes(codes_list, headers, printCodesDone=False):
    global codes_data
    global codes_searched
    lastPrintStatement = time.time()

    for code in set(codes_list):
        passcode = "" # initialize passcode string

        for num in code:
            passcode += str(num) + "," # seperate each number in code with comma

        passcode = passcode[:len(passcode) - 1] # remove last comma from end of string
        joinInfodata["passcode"] = passcode # set data parameters
        joinInfUurl = "https://discovery.minecrafteduservices.com/joininfo"

        r = make_request(joinInfUurl, headers)

        if r == None:
            return

        if r.status_code == 404: # we searched the code, it doesn't exist
            codes_searched.append(code)
        elif r.status_code == 401: # we need a new token, or we need to request again
            if "jwt expired" in r.text:  # we need a new access token
                print("Jwt token expired.")
                return
        elif r.status_code == 200: # we found a code!
            codes_searched.append(passcode)
            server_data = json.loads(r.text)
            ip = server_data["externalIp"]
            world = server_data["serverName"]

            if not ip in codes_data: # if new ip
                print(f"\n\"{world}\" IP: {ip}")
                passcodes = [f"{get_pass_names(passcode)} ({passcode})"]
                server_data["passcodes"] = passcodes
                codes_data[ip] = server_data
                write_codes()
            else: # if it's there already
                passcodes = codes_data[ip]["passcodes"]
                passcodes.append(f"{get_pass_names(passcode)} ({passcode})")
                server_data["passcodes"] = passcodes
                codes_data[ip] = server_data
                write_codes()

        elif r.status_code != 410: # random status code (410 is just "Routing table entry has expired")...
            print("\nUnexpected status code..\n")
            print(r.content)
            print(r.status_code)
        
        if printCodesDone and time.time() - lastPrintStatement >= 10: # wait 10 seconds before printing
            print(f"{len(codes_searched)} codes searched so far.")
            lastPrintStatement = time.time() # reset timer

def find_codes_threading(possible_codes, threads, token, headers):
    print(f"\nSearching {len(possible_codes)} codes!")
    print(f"\nThe time is now {time.ctime(time.time())}\n")
    joinInfodata["accessToken"] = token
    code_threads = [] # stores all threads that are searching for codes
    
    if threads == 0:
        my_chunks = [possible_codes]
    else:
        my_chunks = list(divide_chunks(possible_codes, int(len(possible_codes) / threads)))

    firstThread = True

    for chunk in my_chunks: # search each chunk of split codes, a chunk for each thread
        code_thread = threading.Thread(target=find_codes, args=(chunk,headers,firstThread))
        print(f"Starting thread {code_thread.getName()} with {len(chunk)} requests.")
        code_thread.start()
        code_threads.append(code_thread) # we'll need to check if all threads stopped first

        if firstThread == True:
            firstThread = False

    for thread in code_threads:
        thread.join()    
    
    # ask user for new access token
    print(f"The time is now {time.ctime(time.time())}\n")
    new_token = input("\nPlease enter a new access token (or \"same\"): ")

    if new_token.lower() == "same":
        new_token = token
    else:
        f = open("mc token.txt","w")
        f.write(new_token)
        f.close()

    new_possible_codes = possible_codes
    
    # remove codes that were already searched from new possible codes
    for searched_code in codes_searched:
        if searched_code in new_possible_codes: # if one of the codes we searched is
            new_possible_codes.remove(searched_code) # in new possible codes, remove it

    if len(new_possible_codes) > threads:
        find_codes_threading(new_possible_codes, threads, new_token, headers)
    elif len(new_possible_codes) == 0: # no codes
        print("Done searching all codes!")
        return
    else: # if we have less codes than threads
        print("Almost done searching!")
        find_codes_threading(new_possible_codes, 0, new_token, headers)

def main():
    threads = 40 # os.cpu_count()
    f = open("mc token.txt","r")
    accessToken = f.read()
    f.close()

    codeLength = 4  # length of server code
    numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17] # possible values in each code
    codePermutations = list(itertools.permutations(numbers, codeLength))
    find_codes_threading(
        codePermutations, # possible codes
        threads, # threads
        accessToken, # accessToken
        user_headers # headers
    )

if __name__ == '__main__':
    main()