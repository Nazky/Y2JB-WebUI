<center><h1>Y2JB-WebUI</h1></center>
<center><h2>Manage Y2JB using a WebUI</h2></center>

---

# F.A.Q

### What is this thing ?
This is a local website that allow you to manage everything related to Y2JB easily, with this you can upload, delete and send payloads to you'r console. Payloads can be organized into subdirectories (like `payloads/js/`) and the UI will automatically find them.
### How can i upload a payload ?
You just have to select (or drag and drop) a payload then click on the "upload a payload" button. **You can also download payloads directly from a URL using the input field next to file selection.** These URL downloads are automatically saved to your Repository Manager for future updates.
### How can i send a payload ?
To send a payload that you have uploaded simply click on the "Load payload" button.
### How can i delete a payload ?
If you want to disable a payload from being load using the youtube app, simply click on the "Delete" button.
### Why using this and not [Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) ?
[Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) was a inspiration for this project the downside is to use FTP or a USB drive to update any files, with Y2JB-WebUI you can modify everything on the fly, no need to connect to FTP, using a USB drive or even to have the console power on.
### Is this project compatible with [Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) ?
Well not right now, i maybe fixing that in a next update.
### Do i still need to have Y2JB installed on my console ?
Yes of course, this is not a replacement of [Y2JB](https://github.com/Gezine/Y2JB), make sure to install it first.
### How do I update payloads from GitHub?
Use the **"Select Update"** menu in the navigation bar to choose which payloads to update. Repository configurations (Direct URL or GitHub Release) can be managed via the **"Repos"** button in the navigation bar. The system uses `repos.json` to track and fetch the latest versions.
### Does this work with...
You need something to host the server (pc, raspeberry pi, phone, ...) once the server is up you can access the WebUI from anything that can display a webpage (Android, IOS, PC, Nintendo Switch, ...).
### Can i upload any payload ?
All accepted files are bin, elf and js files.

# How to install

## Windows

First make sure to have [Python](https://www.python.org/downloads/) installed, once is done you can simply double click on **setup_and_run.bat** everything should install automaticlly.

## Linux/MacOS

Exactly like Windows make sure to have [Python](https://www.python.org/downloads/), once is done open a terminal in the root directory and run **setup_and_run.sh** everything should install automaticlly (you maybe have to install Python-venv manually).

## Docker

If you prefer to run everything inside a docker container it's possible, make sure to have [Docker](https://www.docker.com/) installed, once it's done open a terminal and run:
```bash
docker compose up -d
```

<h3 style="color: #ff0000;">⚠️ DO NOT USE THE IPV4 FROM THE DOCKER CONTAINER, USE THE IPV4 OF THE HOST ⚠️</h3>

To know you'r IPV4 on windows open a terminal and run:
```batch
ipconfig
```

To know you'r IPV4 on linux open a terminal and run:
```bash
ip addr show | grep inet
```
Or use **ifconfig**.

## Access WebUI
To access the WebUI simply put you'r **IPV4** with the port **8000** (or a custom one if you change it). 

DO NOT USE **HTTPS** !

Exemple:
```
http://192.168.0.5:8000
```
<h3 style="color: #ff0000;">⚠️ YOU NEED TO HAVE "kstuff.elf" AND "lapse.js" INSIDE THE "payloads" FOLDER ⚠️</h3>

## Configuration
First make sure to put the IP of you'r console when it's done you can click on the "Start Jailbreak" button.

<h3 style="color: #ff0000;">⚠️ DO NOT CHECK THE "Auto-Jailbreak" BEFORE PRESSING THE "Start Jailbreak" BUTTON ⚠️</h3>

If you did check the "Auto-Jailbreak" before pressing the "Start Jailbreak" button and you have problems simply refresh the page, if you still have issues uncheck "Auto-Jailbreak" and restart the server.


## Credits

- [Gezine](https://github.com/Gezine) | [Y2JB](https://github.com/Gezine/Y2JB/)
- [itsPLK ](https://github.com/itsPLK) | [ps5_y2jb_autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader)
- [EchoStretch](https://github.com/EchoStretch) | [kstuff](https://github.com/EchoStretch/kstuff)
- [voidwhisper-ps](https://github.com/voidwhisper-ps) | [ShadowMount](https://github.com/voidwhisper-ps/ShadowMount)
- [drakmor](https://github.com/drakmor) | [ftpsrv](https://github.com/drakmor/ftpsrv)
  

## TODO
- [ ] Add Y2JB auto update (download0.dat)
- [ ] Add Y2JB update blocker option (appinfo.db, param.json, app.db)
- [X] Add repo management (to automaticlly update payloads)
- [X] Add support to load custom js
- [X] Add recursive payload scanning
- [ ] Make it compatible with [ps5_y2jb_autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) (not sure if it's possible)