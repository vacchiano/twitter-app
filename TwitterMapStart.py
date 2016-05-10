#Dominic Vacchiano
#Homework 11
#22C80/104 Programming for Informatics

import Tkinter
import math
import urllib
import json
import oauth2 as oauth


# 
# The code in this file won't work until you set up your Twitter "app"
# at https://dev.twitter.com/apps
# After you set up the app, copy the four long messy strings and put them here.
#
CONSUMER_KEY = "4GVmGzSwfJxO6vn4wFqlVA"
CONSUMER_SECRET = "JTgs1WlBZsJ3kPWqjIpwec5SqsB4TzYMDCpkxH83ks"
ACCESS_KEY = "419281231-ca982bZZOlaTs1HTly2nAcPGQqwl4DEcyQFlZ82R"
ACCESS_SECRET = "aE9JBkqebnebvyrJzXBkZ0ReDpXZcZei1OqmCnotsnlLd"

# Call this function after starting Python.  It creates a Twitter client object (in variable client)
# that is authorized (based on your account credentials and the keys above) to talk
# to the Twitter API
#
def authTwitter():
    
    global client   
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
    client = oauth.Client(consumer, access_token)


# I won't carefully document the functions below.  Study the Twitter REST API to understand
# them and modify them and/or write new ones for different kinds of queries.
#

# e.g. searchTwitter("herky")
#        searchTwitter("snowden")
#
def searchTwitter(searchString, perpage = 15, latlongcenter = None):
    global response
    global data
    global resultDict
    global tweets
    
    addressString = entryText.get()
    centerGeo = geocodeAddress(addressString)   
    
    tweetList = []
    tweetGeoList = []
    
    query = "https://api.twitter.com/1.1/search/tweets.json?q=" + searchString + "&count=" + str(perpage)

    if latlongcenter != None:
        radius = 10 # hardcode a radius of 10km.  Better to generalize this ...
        query = query + "&geocode=" + str(latlongcenter[0]) + "," + str(latlongcenter[1]) + "," + str(radius) + "km"

    response, data = client.request(query)
    resultDict = json.loads(data)
    #print resultDict['statuses']
    # The key information in resultDict is the value associated with key 'statuses' (Twitter refers to
    # tweets as 'statuses'
    tweets = resultDict['statuses']
    for tweet in tweets:
        #print tweet['coordinates']
        tweetList.append(tweet['text'])
        if tweet['coordinates'] == None:
            tweetGeoList.append(centerGeo)
        else:
            tweetGeoList.append(tweet['coordinates']['coordinates'])
        
    #print tweetGeoList[i] 
            #tweetGeoList[i] = 0
            
    #print tweetGeoList
    
    return tweetList, tweetGeoList
        

def whoIsFollowedBy(screenName):
    global response
    global resultDict
    
    query = "https://api.twitter.com/1.1/friends/list.json?&count=20"
    query = query + "&screen_name={}".format(screenName)
    response, data = client.request(query)
    resultDict = json.loads(data)
    for person in resultDict['users']:
        print person['screen_name']
    
def getMyRecentTweets():
    global response
    global data
    global statusList 
    query = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    response, data = client.request(query)
    statusList = json.loads(data)
    for tweet in statusList:
        print tweet['text']
        print

# To use, see the last function in this file, startGUI().

tmp_map_file = 'googlemap.gif'

# Given a string representing a location, return 2-element 
# [latitude, longitude] list for that location 
#
# See https://developers.google.com/maps/documentation/geocoding/
# for details
#
def geocodeAddress(addressString):
   urlbase = "http://maps.googleapis.com/maps/api/geocode/json?"
   args = urllib.urlencode({'address': addressString, 'sensor': 'false'})
   url = urlbase + args
   resultFromGoogle = urllib.urlopen(url).read()
   jsonresult = json.loads(resultFromGoogle)
   if (jsonresult['status'] != "OK"):
      print "Status returned from geocoder *not* OK: {}".format(jsonresult['status'])
      return
   loc = jsonresult['results'][0]['geometry']['location']
   return [float(loc['lat']),float(loc['lng'])]

#
# Google will also "reverse geocode." That is, you can provide a latitude and longitude and
# and Google will try to provide "human readable" information about that location.
#
# Again, see https://developers.google.com/maps/documentation/geocoding/
#
def geocodeLatLng(lat, lng):
   urlbase = "http://maps.googleapis.com/maps/api/geocode/json?"
   llstring = "{},{}".format(lat,lng)
   args = urllib.urlencode({'latlng': llstring, 'sensor': 'false'})
   url = urlbase+args
   resultFromGoogle = urllib.urlopen(url).read()
   jsonresult = json.loads(resultFromGoogle)
   if (jsonresult['status'] != "OK"):
      print "Status returned from geocoder *not* OK: {}".format(jsonresult['status'])
      return
   loc = jsonresult['results'][0]['formatted_address']
   return loc
  
# First construct a URL suitable for the Google Static Maps API
# Then use the URL to request a map from Google, storing the 
# resulting image in tmp_file
# 
def retrieveStaticMap(width, height, lat, long, markerLatLongs, zoom):
   if len(markerLatLongs) > 0:
       url = updateTweetUrl(width, height, lat, long, markerLatLongs, zoom)
   else:
       url = getMapUrl(width, height, lat, long, markerLatLongs, zoom)
   urllib.urlretrieve(url, tmp_map_file)
   return tmp_map_file

# Contruct a Google Static Maps API URL for a map that:
#   has size width x height in pixels
#   is centered at latitude lat and longitude long
#   is "zoomed" to the give Google Maps zoom level (0 <= zoom <= 21)
#    
def getMapUrl(width, height, lat, lng, markerLatLongs, zoom):
   urlbase = "http://maps.google.com/maps/api/staticmap?"
   params = "center={},{}&zoom={}&size={}x{}&format=gif&sensor=false".format(lat,lng,zoom,width,height)
   return  urlbase+params

# Create a map image, built via Google Static Maps API, based on the location
# specified by "addressString" and zoomed according to the 
# given zoom level (Google's zoom levels range from 0 to 21).
# The location will be in the center of the map.
#
def createMapFromAddress(addressString, zoom, markerLatLongs):
   latLong = geocodeAddress(addressString)
   retrieveStaticMap(400, 400, latLong[0], latLong[1], markerLatLongs, zoom)

##########
#
# Most of the code from here down to the GUI section can be ignored on your
# first look.
#
# Code below is extended/modified/adapted from code found
# at http://wiki.forum.nokia.com/index.php/PyS60_Google_Maps_API
#
# some code useful for lat/long <--> x/y conversion
#
magic_number = 128<<21 # this is half the earth's circumference *in pixels* at Google zoom level 21
radius = magic_number / math.pi

# Return a list [winX, winY] of window coordinates corresponding to the 
# given lat/long location for a google map of winWidth-by-winHeight pixels
# centered at lat/long [winCenterLat, winCenterLng] and with the given zoom level
#
# This function should make it easy to place additional text on your maps
#
def latLongToWindowXY(lat, lng, winCenterLat, winCenterLng, winWidth, winHeight, zoom):
   winCenterX = winWidth/2
   winCenterY = winHeight/2
   winX = winCenterX + ((longToGoogleX(lng) - longToGoogleX(winCenterLng))>>(21-zoom))
   winY = winCenterY + ((latToGoogleY(lat) - latToGoogleY(winCenterLat))>>(21-zoom))
   return [winX, winY]

def longToGoogleX(lng):
   return int(round(magic_number + (lng / 180.0) * magic_number))
 
def latToGoogleY(lat):
   return int(round(magic_number -
                    radius * math.log( (1 + math.sin(lat * math.pi / 180)) /
                                       (1 - math.sin(lat * math.pi / 180)) ) / 2))
 
def googleXToLong(x):
   return 180.0 * ((round(x) - magic_number) / magic_number)
 
def googleYToLat(y):
   return ( (math.pi / 2) - (2 * math.atan(math.exp( (round(y)-magic_number)/radius ))) ) * 180 / math.pi
  
########## 
# very basic GUI code

markerLatLongs = []
defaultLocation = "Iowa City, IA"

def readEntryAndShowMap():
   #### you should change this function to read from the location from an Entry widget
   addressString = defaultLocation
   addressText = entryText.get()
   if addressText != "":
       addressString = entryText.get()
   if TwitterEntryText.get() != "":
       markerLatLong = getTweetGeo()

   createAndDisplayMap(addressString, markerLatLong)

    
def createAndDisplayMap(addressString, markerLatLongs):
    #if TwitterEntryText.get() != "":
        #markerLatLongs = getTweetGeo()
    #print MarkerLatLongs
    createMapFromAddress(addressString, zoomValue.get(), markerLatLongs)
    mapImage = Tkinter.PhotoImage(file=tmp_map_file)
    mapLabel.image = mapImage
    mapLabel.configure(image=mapImage)
    if TwitterEntryText.get() != "":
        getTweet()
   
   
    return
  
def getTweet():
    global latLongs
    address = entryText.get()
    LatLongs = geocodeAddress(address)
    tweetNum = (tweetNumValue.get() - 1)
    #print tweetNum
    tweetText = TwitterEntryText.get()
    #print tweetText
    #print LatLongs
    tweet, tweetGeo = searchTwitter(tweetText, 15, LatLongs)
    
    markerLatLongs = tweetGeo[tweetNum]
    #print markerLatLongs[0]
            
    displayableText = ((tweet[tweetNum]).encode('utf-8'))
    tweetTextValue.set(displayableText)
    #print tweetGeo
    updateTweet()
    #return tweetGeo
    
def getTweetGeo():
    global latLongs
    address = entryText.get()
    LatLongs = geocodeAddress(address)
    tweetNum = (tweetNumValue.get() - 1)
    #print tweetNum
    tweetText = TwitterEntryText.get()
    #print tweetText
    #print LatLongs
    tweet, tweetGeo = searchTwitter(tweetText, 15, LatLongs)
    #print tweetGeo
    markerLatLongs = tweetGeo[tweetNum]
    #print markerLatLongs[0]
            
    #displayableText = ((tweet[tweetNum]).encode('utf-8'))
    #tweetTextValue.set(displayableText)
    #print tweetGeo
    #updateTweet()
    return markerLatLongs
    
def updateTweet():
    displayText = tweetTextValue.get()
    displayableText = displayText.encode('utf-8')
    tweetTextLabel.configure(text="{}".format(displayableText))
    
def updateTweetUrl(width, height, lat, lng, markerLatLongs, zoom):
    #print 1
    #print markerLatLongs
    urlbase = "http://maps.google.com/maps/api/staticmap?"
    params = "center={},{}&zoom={}&size={}x{}&format=gif&markers=color:red:%7C{},{}&sensor=false".format(lat,lng,zoom,width,height,markerLatLongs[0],markerLatLongs[1])
    return  urlbase+params
  
def zoomIn():
    
    zoom = zoomValue.get()
    if zoom < 22:
        zoom = zoom + 1
    zoomValue.set(zoom)
    updateZoomLabel()
    readEntryAndShowMap()
   
def zoomOut():
    zoom = zoomValue.get()
    if zoom > 0:
        zoom = zoom - 1
    zoomValue.set(zoom)
    updateZoomLabel()
    readEntryAndShowMap()
   
def updateZoomLabel():
   zoomLabel.configure(text="{}".format(zoomValue.get()))
   
def prevTweet():
    tweet = tweetNumValue.get()
    if tweet != 1:
        tweet = tweet - 1
        
    tweetNumValue.set(tweet)
    getTweet()
    updateTweetNumLabel()
    #readEntryAndShowMap()
    
def nextTweet():
    tweet = tweetNumValue.get()
    if tweet != 15:
        tweet = tweet + 1
        
    tweetNumValue.set(tweet)
    getTweet()
    updateTweetNumLabel()
    #readEntryAndShowMap()
    
def updateTweetNumLabel():
    tweetNumLabel.configure(text="{}/{}".format(tweetNumValue.get(), "15"))
  
  
def initializeGUIetc():
    
  
   global rootWindow
   global markerLatLongs
   global zoomValue
   global mapLabel
   global entryText
   global zoomInButton
   global zoomOutButton
   global zoomLabel
   global TwitterEntryText
   global tweetNumLabel
   global prevTweet
   global nextTweet
   global tweetNumValue
   global tweetTextLabel
   global tweetTextValue
   global tweetSearchValue
   global LatLongs



   rootWindow = Tkinter.Tk()

   # not used in this basic version
   markerLatLongs = []
   
   tweetTextValue = Tkinter.StringVar()
   tweetTextValue.set("")
   
   tweetSearchValue = Tkinter.StringVar()
   tweetSearchValue.set("")
   
   zoomValue = Tkinter.IntVar()
   zoomValue.set(12)
   
   tweetNumValue = Tkinter.IntVar()
   tweetNumValue.set(1)

   mainFrame = Tkinter.Frame(rootWindow,width=850) 
   mainFrame.pack()
   
   entryLabel = Tkinter.Label(mainFrame, text="Enter Location:")
   entryLabel.pack()
   
   entryText = Tkinter.Entry(mainFrame, text = "iowa city")
   entryText.pack()
   
   TwitterEntryLabel = Tkinter.Label(mainFrame, text="Enter Tweet: ")
   TwitterEntryLabel.pack()
   
   TwitterEntryText = Tkinter.Entry(mainFrame)
   TwitterEntryText.pack()

   # until you add code, pressing this button won't change the map.
   # you need to add an Entry widget that allows you to type in an address
   # The click function should extract the location string from the Entry widget and create
   # the appropriate map.
   readEntryAndShowMapButton = Tkinter.Button(mainFrame, text="Show me the map!", command=readEntryAndShowMap)
   readEntryAndShowMapButton.pack()

   mapFrame = Tkinter.Frame(mainFrame, width=400, bd=2, relief=Tkinter.GROOVE)
   mapFrame.pack()
   mapLabel = Tkinter.Label(mapFrame)
   createAndDisplayMap(defaultLocation, markerLatLongs)
   mapLabel.pack()
   
   zoomFrame = Tkinter.Frame(mainFrame, width=100, bd = 2)
   zoomFrame.pack(side = "right")
   
   zoomInButton = Tkinter.Button(zoomFrame, text="+", command = zoomIn)
   zoomInButton.pack()
   
   zoomLabel = Tkinter.Label(zoomFrame, text="12")
   zoomLabel.pack()
   
   zoomOutButton = Tkinter.Button(zoomFrame, text="-", command = zoomOut)
   zoomOutButton.pack()
   
   tweetFrame = Tkinter.Frame(mainFrame, width = 300, bd = 2)
   tweetFrame.pack()
   
   tweetNumLabel = Tkinter.Label(tweetFrame, text="1/15")
   tweetNumLabel.pack(side="top")
   
   prevTweet = Tkinter.Button(tweetFrame, text="Previous", command = prevTweet)
   prevTweet.pack(side='left')
   
   tweetTextLabel = Tkinter.Label(tweetFrame, text="Tweet Text Will Appear Here!")
   tweetTextLabel.pack(side="left")
   
   nextTweet = Tkinter.Button(tweetFrame, text="Next", command = nextTweet)
   nextTweet.pack()


def startGUI():
    authTwitter()
    initializeGUIetc()
    rootWindow.mainloop()