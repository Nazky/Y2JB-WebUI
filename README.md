<center><h1>Y2JB-WebUI</h1></center>
<center><h2>Manage Y2JB using a WebUI</h2></center>
<center><a href="https://discord.gg/7CcBNJup2j"><img src="https://img.shields.io/discord/1463591261461155935?color=7289da&label=Discord&logo=discord&logoColor=white" alt="Discord"></a></center>

---

# F.A.Q

### What is this thing ?
This is a local website that allow you to manage everything related to Y2JB easily. It features:
- **Payload Management**: Upload, delete, and send payloads with recursive directory support.
- **Repository Manager**: Automatically update payloads directly from GitHub Releases or URLs.
- **DNS Manager**: Redirect domains (like the User Guide) or block Sony updates via sinkholing.
- **FTP Manager**: Browse, upload, delete, and edit files on your PS5 from the browser. Includes a built-in text editor and image viewer.
- **Settings & Customization**: Configure Auto-Jailbreak, manage Payload Loading Sequence, toggle Dark Mode, and enable specific options like Kstuff autoloading.
- **Automation**: Integrated Auto-Jailbreak with configurable delay and firing order.
- **Tools**: One-click Update Blocker and `download0.dat` push.

### How can i upload a payload ?
You just have to select (or drag and drop) a payload then click on the "upload a payload" button. **You can also download payloads directly from a URL using the input field next to file selection.** These URL downloads are automatically saved to your Repository Manager for future updates.
### How can i send a payload ?
To send a payload that you have uploaded simply click on the "LOAD" button.
### How can i delete a payload ?
If you want to disable a payload from being load using the youtube app, simply click on the trash icon button.
### Why using this and not [Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) ?
[Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) was a inspiration for this project the downside is to use FTP or a USB drive to update any files, with Y2JB-WebUI you can modify everything on the fly, no need to connect to FTP, using a USB drive or even to have the console power on.
### Is this project compatible with [Y2JB Autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) ?
Well not right now, i maybe fixing that in a next update.
### Do i still need to have Y2JB installed on my console ?
Yes of course, this is not a replacement of [Y2JB](https://github.com/Gezine/Y2JB), make sure to install it first.
### How do I update payloads from GitHub?
Navigate to the **Repository Manager** by clicking the **"Repos"** button in the navigation bar. From there, you can add repositories using asset patterns (e.g. `kstuff.elf`) and update individual payloads using the refresh button next to each entry.

### What is the DNS Manager for?
It allows you to intercept console traffic. Usage is explained in the WebUI.

### What can I do with the FTP Manager?
The FTP Manager allows you to manage files on your console without external software. It includes a **built-in text editor** for configuration files and an **image viewer** for standard formats. Keep in mind it's experimental.

### What options are in Settings?
You can configure:
- **Connection**: PS5 IP Address and FTP Port.
- **Automation**: Toggle Auto-Jailbreak and "Load Kstuff" (automatically sends `kstuff.elf` if present).
- **Sequence**: Toggle which payloads auto-load and set a global delay time.
- **Appearance**: Toggle Dark Mode and UI Animations.

### Does this work with...
You need something to host the server (pc, raspeberry pi, phone, ...) once the server is up you can access the WebUI from anything that can display a webpage (Android, IOS, PC, Nintendo Switch, ...).
### Can i upload any payload ?
All accepted files are bin, elf, js and dat files.

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
<h3 style="color: #ff0000;">⚠️ YOU NEED TO HAVE "kstuff.elf" INSIDE "payloads/" AND "lapse.js" INSIDE "payloads/js/" ⚠️</h3>

## Configuration
First make sure to put the IP of you'r console when it's done you can click on the "Start Jailbreak" button. For the **Update Blocker** and **Download0.dat** tools, ensure you also configure the **FTP Port** (Default is 1337).

<h3 style="color: #ff0000;">⚠️ DO NOT CHECK THE "Auto-Jailbreak" BEFORE PRESSING THE "Start Jailbreak" BUTTON ⚠️</h3>

If you did check the "Auto-Jailbreak" before pressing the "Start Jailbreak" button and you have problems simply refresh the page, if you still have issues uncheck "Auto-Jailbreak" and restart the server.


## Credits

- [Gezine](https://github.com/Gezine) | [Y2JB](https://github.com/Gezine/Y2JB/)
- [rmuxnet](https://github.com/rmuxnet) | [Features for the WebUI](https://github.com/rmuxnet/Y2JB-WebUI)
- [itsPLK ](https://github.com/itsPLK) | [ps5_y2jb_autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader)
- [EchoStretch](https://github.com/EchoStretch) | [kstuff](https://github.com/EchoStretch/kstuff)
- [voidwhisper-ps](https://github.com/voidwhisper-ps) | [ShadowMount](https://github.com/adel-ailane/ShadowMount)
- [drakmor](https://github.com/drakmor) | [ftpsrv](https://github.com/drakmor/ftpsrv)
- [john-tornblom](https://github.com/john-tornblom) | [websrv](https://github.com/ps5-payload-dev/websrv)

## Bugs & Feature Requests

If you encounter any bugs or have ideas for new features, please submit them by opening an issue in this repository. Suggestions and feedback are welcome!

## TODO
- [X] Add Y2JB auto update (download0.dat)
- [X] Add Y2JB update blocker option (appinfo.db, param.json, app.db)
- [X] Add repo management (to automaticlly update payloads)
- [X] Add support to load custom js
- [X] Add recursive payload scanning
- [ ] Make it compatible with [ps5_y2jb_autoloader](https://github.com/itsPLK/ps5_y2jb_autoloader) (not sure if it's possible)

## Screenshots

### Main Page
![Main Page](static/img/1.png)

### Repository Manager
![Repository Manager](static/img/2.png)
