#keep demo test printing to check cases
import sys
import twitter
import time
import mraa
import math

#Sets pin 29 on dragonboard as output (buzzer)
buzz = mraa.Gpio(29)
buzz.dir(mraa.DIR_OUT)

#Sets pin 31 on dragonboard as input (touch sensor)
touch = mraa.Gpio(31)
touch.dir(mraa.DIR_IN)

#Input for setting alarm time
print("What time would you like your alarm? (24 hour format)")
hour = int(input("Enter the hour: "))
minute = int(input("Enter the minute: "))
second = int(input("Enter the second: "))

hour = hour - 19
if hour < 0:
    hour = 24 + hour

bus = input("Do you want the alarm to turn off if buses are cancelled? (Y/N) ")

#Accessing the twitter API
api = twitter.Api(consumer_key="3cpzpSjpcu5mF1GEKWUMopyeW",
                      consumer_secret="3Hjh8i3O1aWZUsbrD27r8h3HKPrnD8hgpYo7b8zojNMWt8qLLs",
                      access_token_key="838169904499015681-9OQ5Xl6yVQK6IBhJKT62AYpYluxtUGd",
                      access_token_secret="J5hiTjjKRZ4ATU3tF4r1LhO86Az8NZbgtcKtQGbd6QQJe")

kevin = 838169904499015681
peel = 23796987

statuses = api.GetUserTimeline(kevin)
old = statuses[0].text

alarm = True

#main running loop
while True:
    buzz.write(0)
    statuses = api.GetUserTimeline(kevin)
    new = statuses[0].text
    if new != old:  #checking for new recent tweets
        print("New tweet")
        old = new
        if bus == "Y":  #finding if keywords 'school', 'close', 'cancel', and 'bus' are in the new tweet 
            if ("school" in new and ("close" in new or "cancel" in new)) or ("bus" in new and "cancel" in new):
                alarm = False
            else:
                alarm = True
        else:        
            if "school" in new and ("close" in new or "cancel" in new):
                alarm = False
            else:
                alarm = True

    #alarm goes off at set time if alarm is on
    if time.localtime().tm_hour == hour  and time.localtime().tm_min == minute and time.localtime().tm_sec >= second:
        snooze = False
        while True:
            if alarm:   
                buzz.write(1)   #buzz if alarm was turned on
                otherstart = time.time()
                press = False
                while True:
                    #print (tick)
                    #print (pause)
                    cur = time.time()
                    #pause+=1
                    if math.floor(cur - otherstart) % 2 == 0:
                        buzz.write(0)
                    else:
                        buzz.write(1)
                        
                    touchbutton = int(touch.read())
                    if touchbutton == 1 and not press:
                        start = time.time()
                        #tick+=1
                        press = True
                    
                    if press:
                        if cur - start > 2: #press and hold sensor for 2 seconds to turn off alarm, or else snooze alarm on press
                            snooze = False
                            alarm = False
                            break
                        
                    if touchbutton == 0 and press:
                        snooze = True
                        break
                    """if press:
                        if cur - start > 3: #press and hold sensor for 2000 ticks to turn off alarm, or else snooze alarm on press
                            snooze = False
                            alarm = False
                            break
                    
                    elif press and touchbutton == 0:
                        snooze = True
                        break"""
                
                alarm = False
            else:
                if snooze:
                    print ("snooze")
                    buzz.write(0)
                    time.sleep(10)
                    alarm = True
                else:
                    print("off")
                    break

    #resets alarm every  night at 12:00 am
    if time.localtime().tm_hour == 0  and time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
        alarm = True

