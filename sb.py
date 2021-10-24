#!/usr/bin/python3

import time
from datetime import datetime
from threading import Thread
import requests
import textwrap

from evdev import InputDevice, categorize, ecodes
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from LMSTools import LMSServer, LMSPlayer
import screencontrols as scr

SERVER = '192.168.68.xxx' ip address of Logitech Media Server
PORT = '9000'
PLAYER = 'xx:xx:xx:xx:xx:xx'  # MAC Address of player

## AirNow zipcode
AQI_ZIP = '99999'
## AirNow API Key 
AQI_KEY = 'XXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
## AirNow URL
AQI_URL = "https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode={}&API_KEY={}".format(AQI_ZIP,AQI_KEY)

## OpenWeatherMap API Key
OWM_KEY = 'xxxxxxxxxxxxxxxxxxxx'
## OpenWeatherMap City ID
OWM_ID = '9999999'
## OpenWeatherMap URL 
OWM_URL = "http://api.openweathermap.org/data/2.5/weather?units=imperial&id={}&appid={}".format(OWM_ID,OWM_KEY)

## Touchscreen event worker thread
def event_thread():
  for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
      absevent = categorize(event)
      if absevent.event.value == 0:
        handle_event(dev)


## Red and Blue color channels are reversed from normal RGB on pi framebuffer
def swap_redblue(img):
  r, g, b, a = img.split()
  return Image.merge("RGBA", (b, g, r, a))

## Paint image to screen at position
def blit(img, pos):

  size = img.size
  w = size[0]
  h = size[1]

  img = swap_redblue(img)
  fb.seek(4 * ((pos[1]) * fbw + pos[0]))

  iby = img.tobytes()
  for i in range(h):
    fb.write(iby[4*i*w:4*(i+1)*w])
    fb.seek(4 * (fbw - w), 1)

## Clear the screen, set backlight brightness
def initscreen():

  # set screen brightless
  try:
    scr.screenon()
  except Exception:
    pass

  img = Image.new('RGBA', (800, 480))
  draw = ImageDraw.Draw(img)

  blit(img,(0,0))

## Color song progress line
def displayprogress(seek, duration, color):

  if duration > 0:
    progress = seek / duration * 800
  else:
    progress = 0

  img = Image.new('RGBA', (800, 6))

  draw = ImageDraw.Draw(img)
  draw.line((0,0,progress,0),fill=color,width=6)

  blit(img,(0,44))

  ## Display AQI color bar above date/time
  img = Image.new('RGBA',(370,6))

  draw = ImageDraw.Draw(img)
  draw.line((0,0,370,0),fill=color,width=6)
  blit(img,(430,430))

## Date time bar, bg color arg
def displaydatetime(color):

  img = Image.new('RGBA', (370,50),color=(0,0,0,255))
  draw = ImageDraw.Draw(img)
  
  try:
    temp = '{}\u00b0'.format(int(owm['main']['temp']))
    dt = datetime.now().strftime("%a, %b %d %-I:%M ")
    disp = dt + temp

    draw.text((13,7),disp,'white',font=fonts[1])
    blit(img,(430,430))
  except:
    pass

## Display artist, song title, album title
def displaymeta(data):

  img = Image.new('RGBA',size=(370,430),color=(0,0,0,255))

  tw1 = textwrap.TextWrapper(width=15)
  tw2 = textwrap.TextWrapper(width=20)
  s = "\n"

  try:
    artist = data['artist']
  except:
    artist = ""

  try:
    title = data['title']
  except:
    title = ""

  try:
    album = data['album']
  except:
    album = ""

  if artist is None: 
    artist = ""
  if title is None:
    title = ""
  if album is None:
    album = ""

  artist = s.join(tw2.wrap(artist))
  album = s.join(tw2.wrap(album))

  draw = ImageDraw.Draw(img)

  draw.text((10,50), artist, (191,245,245),font=fonts[1])
  draw.text((10,250), album, (255,255,255),font=fonts[1])

  blit(img,(430,0))

  img = Image.new('RGBA',size=(800,50),color=(0,0,0,255))
  draw = ImageDraw.Draw(img)
  draw.text((0,0),  title, (255,255,255),font=fonts[0])

  blit(img,(0,0))

## Get album cover art and display it
def getcoverart(cover_url):

  try:
    img = Image.open(requests.get(cover_url, stream=True).raw)
    img = img.resize((430,430))
    img = img.convert('RGBA')

    blit(img,(0,50))
  except Exception as e:
    print(e)
    pass

## Handle touchscreen events
def handle_event(dev):

  x1 = dev.absinfo(ecodes.ABS_X).value
  y1 = dev.absinfo(ecodes.ABS_Y).value

  ## Calculate actual x,y position touched
  x=800-int((y1/480)*800)
  y=480-int(480-(x1/800)*480)

  scr.screenon()

  try:
    playing = (player.mode == "play")
    ## Bottom right touched - next
    if x> 400 and y> 240:
      player.next()
    ## Top of screen touched - pause/play
    elif y<240:
      if playing:
        player.pause()
        playing = False
      else:
        player.unpause()
        playing = True
    ## Bottom left touched - prev
    elif x<400 and y>240:
      player.prev()
  except Exception:
    pass

## OpenWeatherMap thread
def get_owm():
  global owm

  while True:
    try:
      owm = requests.get(OWM_URL).json()
    except:
      pass

    time.sleep(300)

## AirNow thread
def get_aqi():

  global aqi_color  

  while True:
    try:
      json = requests.get(AQI_URL).json()
      for j in json:
        if j['ParameterName']=='PM2.5':
          aqi=j['AQI']
          break

      if aqi <= 50:
        aqi_color = 'green'
      elif aqi <= 100:
        aqi_color = 'yellow'
      elif aqi <= 150:
        aqi_color = 'orange'
      elif aqi <= 200:
        aqi_color = 'red'
      elif aqi <= 300:
        aqi_color = 'purple'
      else:
        aqi_color = 'maroon'
    except:
      pass

    ## Sleep 30 minutes
    time.sleep(1800)  

fonts = []
fonts.append( ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30) )
fonts.append( ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 28) )
fonts.append(  ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 18) )

nowplaying = ''
old_nowplaying = ''
cover_url = ''
old_url = ''
old_playing = False
seek = 0
duration = 60
progress = 0
aqi_color = 'green'
owm = {}
playing = True
detail = []

fbw, fbh = 800, 480   # framebuffer dimensions
fb = open("/dev/fb0", "wb")

## Touchscreen input device
dev = InputDevice('/dev/input/event0')

## Start event handler thread
t = Thread(target=event_thread)
t.start()

t1 = Thread(target=get_aqi)
t1.start()

t2 = Thread(target=get_owm)
t2.start()

## Init LMS connection
server = LMSServer(SERVER)
player = LMSPlayer(PLAYER, server)

## Clear the screen
initscreen()
displaydatetime(aqi_color)

## Main loop 
while True:
  try:
      playing = (player.mode == "play")

      if playing:
        try:
          detail = player.playlist_get_current_detail(amount=1)[0]
          seek = player.time_elapsed
          duration = player.track_duration
          displayprogress(seek,duration,aqi_color)
        
          if 'artwork_url' in detail:
            artwork_url = detail['artwork_url']
            if not artwork_url.startswith('http'):
              if artwork_url.startswith('/'):
                artwork_url = artwork_url[1:]

              cover_url = 'http://{}:{}/{}'.format(SERVER,PORT,artwork_url)
            else:
              cover_url = artwork_url
          else:
            cover_url='http://{}:{}/music/{}/cover.jpg'.format(SERVER,PORT,detail['artwork_track_id'])
        except Exception as e:
          print(e)
          pass

        nowplaying = detail['title']

      if not playing:
        scr.screenoff()
        displayprogress(0,duration,aqi_color)
        old_playing = playing

      if playing != old_playing:
        old_playing = playing
        if playing:
          scr.screenon()

      if nowplaying != old_nowplaying:
        old_nowplaying = nowplaying
        getcoverart(cover_url)
        scr.screenon()
        displaymeta(detail)

      if cover_url != old_url:
        old_url = cover_url
        getcoverart(cover_url)
        scr.screenon()

      time.sleep(1)

      if (time.time() % 60) <= 1.0:
        displaydatetime(aqi_color)

  except Exception as e:
    print(e)
    pass
