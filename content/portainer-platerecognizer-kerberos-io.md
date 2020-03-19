Title: Platerecognizer SDK with Kerberos.io and Portainer on a Raspberry PI
Date: 2020-03-19 13:46
Modified: 2020-03-19 13:50
Category: rpi
Tags: docker, rpi
Slug: portainer-kerberos-io-platerecognizer
Authors: wossname?
Summary: Installing the Platerecognizer API on a Raspberry PI, feeding it with pictures/video from Kerberos.io container on the same PI



Install Docker & Portainer:
https://homenetworkguy.com/how-to/install-pihole-on-raspberry-pi-with-docker-and-portainer/
(Pi-Hole is also handy, but not for this project)
For good instructions on installing Portainer, follow the above tutorial.
Here's a summary:
 
On the Raspberry Pi command line:
*	Install Docker on the 
    * 	curl -sSL https://get.docker.com | sh
    *	 sudo usermod -aG docker pi
    *	Log out & in again
    *	If the usermod doesn’t “take”, you need to add “sudo” before all the commands below
*	Install Portainer:
    *	docker volume create portainer_data
    *	docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data --restart always portainer/portainer
    *	Check that Portainer is running:
    *	docker ps
    *	Check that you can connect: 
    *	Point your web browser to the PI ip adress, port 9000
*	You will need to create an admin user. 
    The GUI doesn't really give the impression that you can change the username, but you can. 
    I used the  username "pi" so there's one less to remember
*	After login, select "Local" and click "Connect"
 
Portainer is now good to go, and you can install Platerecognizer SDK.
Register at Platerecognizer to get a token and SDK API Key (They provide trial SDK keys on request)

*	Install Platerecognizer using Portainer GUI:
    *	Create a volume:
    *	license
    *	Create container:
    *	Image: platerecognizer/alpr-raspberry-pi
    *	Manual network port publishing:
    *	Manual network port publishing:
    *	8080 -> container 8080
*	Add volume: 
    *	Container: /license
    *	-> volume: license-local
*	Add environment variables:
    TOKEN=UAUAVzugJEq6I3kKAvhswOcWqg7mhxGNtjsZrYd2 (replace with your token)
    LICENSE_KEY=XdVhbZI3I (Replace with your license)
*	Restart policy: Restart unless stopped
    *	Check that Platerecognizer is working:
*	http://localhost:8080/info/
*	Check that ANPR is working using the Raspberry PI command line:
    *	curl -o /tmp/car.jpg https://app.platerecognizer.com/static/demo.jpg
    *	curl -F 'file=@/tmp/car.jpg' http://localhost:8080/alpr
    *	You should get some JSON output:
    *	{"processing_time": 1571.571, "camera_id": null, "filename": "car.jpg", "usage": {"max_calls": 5000, "calls": 4503}, "results": [{"vehicle": {"type": "Car", "box": {"ymin": 116, "xmax": 923, "ymax": 659, "xmin": 90}, "score": 0.811}, "box": {"ymin": 483, "xmax": 281, "ymax": 581, "xmin": 150}, "region": {"code": "gb", "score": 0.979}, "candidates": [{"score": 0.895, "plate": "nhk552"}], "dscore": 0.83, "score": 0.895, "plate": "nhk552"}], "timestamp": "2020-03-15 12:29:21.591831"}
    *	Want to have it human-readable? jq is your friend:
    *	sudo apt install jq
    *	anpr=$(curl -s -F 'file=@/tmp/car.jpg' http://localhost:8080/alpr)
    *	echo $anpr | jq .results[]

*	Install Kerberos.IO (more info here: http://doc.kerberos.io/opensource/installation)	
    *	Create a volume, for easy local access to images and videos created by Kerberos.io
    *	Example name: kerberos
    *	Create container:
    *	A sensible name. if your IP-camera has a name on the network, use that.
    ...or a sensible unique identifier, example: "kerberosio-45" since my cameras IP address ends in .45
*	Image: kerberos/kerberos
*	Volumes:
    *	Container: /etc/opt/kerberosio/capture ->volume kerberos - local
*	Manual network port publishing:
    *	89 -> 80
    *		8889 -> 8889
*	Restart policy: Unless stopped
*	Point your web-browser to the Raspberry PI ip, port 89
*	First select language, then create user/password
*	Click "Configuration" and give the container a name
*	Select "IP Camera" and input the stream URL. 
    It can be challenging to find.
    This tool worked well for me: https://sourceforge.net/projects/onvifdm/
    For my Chinese HIKVISION knockoff it is:
    *	rtsp://172.16.172.39:554/11
    *	You want to use the RPI camera? Then you'll need to either setup fast mpjpeg-streamer or suchlike in the host OS, or install a container that provides an IP stream from the RPICam
*	Select a suitable resolution, delay and framerate
    Note: Kerberos.io seems to REALLY like that you use the same resolution and framerate that the camera sends)
*	Click Confirm & Select, and then Update
    Note: The Kerberos.io GUI is kinda weird: 
    *	you navigate with the small arrows in the popup window
    *	you MUST click "Update" for changes to be saved
*	Go to the Dashboard and check if stream is working.
    Be advised; it may take a LONG time before the stream shows up. Minutes, easily.
*	Now you need to "tune" Kerberos.io to give you correct trigger. Play with detection zone, delay, fps etc.
*	Once you are happy with captured images, it is time to run them through Platerecognizer
    *	Where are the images, you ask? /var/lib/docker/volumes/<whateveryounamedit>
*	Open a (root) shell, either from Portainer or from the PI command line
*	Edit the run.sh script (or input another name in the Motion config in Kerberos.io)
    *	apt install nano
    *	nano /etc/opt/kerberosio/scripts/run.sh

Simple example:
---
#!/bin/bash
 
start=$(date +%s%3N)
filnavn=$(echo $1 | jq -r '.pathToImage')
alpr=$(curl -s -F 'file=@/etc/opt/kerberosio/capture/'$filnavn'' http://192.168.172.51:8080/alpr)
stopp=$(date +%s%3N)
 
echo "---" >>/tmp/motion.log
echo $(date -d @$((start/1000)) +"%Y%m%d %H:%M:%S") $filnavn >>/tmp/motion.log
echo "ANPR-prosessering ms: " $(($stopp-$start)) >>/tmp/motion.log
echo $alpr >>/tmp/motion.log
 
* Now you have ANPR results in /tmp/motion.log. 

Run.sh would be the fastest way to get something done on ANPR results; 
for instance: opening a gate for a known license plate

For general use however, a script monitoring the volume (locally on PI: /var/lib/docker/volumes/kerberos/_data ) using inotify or suchlike would be better. 

One could also consider using a AI system/Machine Learning to determine if a vehicle is in the image before running it through ANPR, to save on the number of calls to the Platerecognizer SDK

Note: The ANPR results include "area of interest", which can be used for many interesting things, including determining the vehicle direction of travel, if you set up motion on Kerberos.io to capture several pictures of the moving car.

Kerberos can capture video also, but Platerecognizer uses on API call per frame, so it's really not a good idea to use Platerecognizer on video until they find a better solution for this (…unless you have an SDK with unlimited calls)
 

