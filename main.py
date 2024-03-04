from flask import Flask, render_template, Response, request
from PIL import Image, ImageDraw, ImageFont
import numpy
import cv2
import math
app = Flask(__name__,static_url_path='/static')

class rgb:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

p1 = rgb(0,0,0)

chars = "_.,-=+:;cba|?0123456789$W#@"[::-1]
charArray = list(chars)
charLength = len(charArray)
interval = charLength / 256

scaleFactor = 0.09

oneCharWidth = 10
oneCharHeight = 18

def getChar(inputInt):  #returns the closest number in char array to that specific average since we dont have 255 chars in the chars array
    return charArray[math.floor(inputInt * interval)]

fnt = ImageFont.truetype('C:\\Windows\\Fonts\\lucon.ttf', 15)

# Function to capture video from the camera
camera = cv2.VideoCapture(0)

def gen_frames(camera_index):
    #camera = cv2.VideoCapture(camera_index)  # Change the index to use a different camera (e.g., 1 for a second camera)
    while True:
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
            frame = buffer.tobytes()  # Convert the frame to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame in the HTTP response format
    camera.release()

def gen_ascii_frames(red,green,blue):
    #camera = cv2.VideoCapture(camera_index)  # Change the index to use a different camera (e.g., 1 for a second camera)
    while True:
        success, im = camera.read()
        if not success:
            break
        else:
            # im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            color_coverted = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(color_coverted)
            width, height = im.size
            im = im.resize((int(scaleFactor * width), int(scaleFactor * height * (oneCharWidth / oneCharHeight))),
                           Image.NEAREST)
            pixel = im.load()
            width, height = im.size
            finalImage = Image.new('RGB', (oneCharWidth * width, oneCharHeight * height), color=(0, 0, 0))
            d = ImageDraw.Draw(finalImage)
            for i in range(height):
                for j in range(width):
                    r, g, b = pixel[j, i] #grab the r,g,b for every pixel
                    avg = int((r + g + b) / 3)
                    pixel[j, i] = (r, g, b)
                    if(red==0 and blue ==0 and green==0):
                        d.text((j * oneCharWidth, i * oneCharHeight), getChar(avg), font=fnt, fill=(r, g, b))
                    elif(red==-1 and blue==-1 and green==-1):
                        d.text((j * oneCharWidth, i * oneCharHeight), getChar(avg), font=fnt, fill=(avg, avg, avg))
                    else:
                        d.text((j * oneCharWidth, i * oneCharHeight), getChar(avg), font=fnt, fill=(red, green, blue))

                    # j * oneCharWidth, i * oneCharHeight gives us the location
                    # getchar(avg) gives us the char to put in it's place
                    # font=fnt gives us the specific font we chose
                    # fill=(r,g,b) gives us the color to fill it out as, if we do it avg,avg,avg we'll get black and white.
            finalImage = numpy.array(finalImage)
            finalImage = finalImage[:, :, ::-1].copy()
            ret, buffer = cv2.imencode('.jpg', finalImage)  # Encode the frame as JPEG
            finalImage = buffer.tobytes()  # Convert the frame to bytes
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + finalImage + b'\r\n')  # Yield the frame in the HTTP response format
    camera.release()


@app.route('/', methods = ["GET","POST"])
def index():
    if request.method == "POST":
        p1.red= request.form.get("r")
        p1.green = request.form.get("g")
        p1.blue = request.form.get("b")
    return render_template('index.html')  # Render the HTML template

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')  # Return the video feed as a response

@app.route('/ascii_feed')
def ascii_feed():
    return Response(gen_ascii_frames(int(p1.red),int(p1.blue),int(p1.green)), mimetype='multipart/x-mixed-replace; boundary=frame')  # Return the ascii feed as a response

if __name__ == '__main__':
    app.run(debug=True)
