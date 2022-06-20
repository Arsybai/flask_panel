![img](https://images.arsybai.app/images/UtCGEWYUeP.png)

Just like a CPanel. but it's for python Flask only.
The reason I make this is because my personal problem that I always manually deploy my app to my server.

### Feature
- [x] MySQL Database
- [x] phpMyAdmin
- [ ] File Manager
- [ ] Backup
- [ ] Git
- [ ] SLL Let's encrypt

_note: the unchecked will added soon_

# then, How?
---
### Requirements
- Ubuntu server with `sudo`
- python3
- screen
- a domain that already add `A` record to public server IP
_`Note: Disable proxy, for certbot installation. you can enable it after installation done`_

### Step 1
Clone or download or anything this repo and put to your server.
I recomended here
```
root
 ┗ 📦flask_panel
    ┣ 📂 flask_panel
    ┣ 📜config.json
    ┣ 📜flask_panel.py
    ┣ 📜flask_panel.sql
    ┗ 📜README.md
```

### Step 2
Set up the config file in `config.json`
```json
{
    "admin":{
        "username":"admin",
        "password":".Admin1234"
    },

    "server_name": {
        "flask_panel": "panel.example.com",
        "phpmyadmin":"database.example.com"
    },

    "phpver": "8.1"
}
```
- the `admin` is login access to your flask panel
- the `server_name` is a domain with `A` record to your public server IP. 

Example setting DNS A record
![img](https://images.arsybai.app/images/nRWwXADFna.png)

## Step 3
get into flask_panel directory
```bash
$cd flask_panel
```
and run the installation
```bash
$python3 flask_panel.py
```

if this appear, just hit enter and enter
![img](https://images.arsybai.app/images/bqCvXVNLji.png)
_Note: do not restart it_

if this appear, press tab until the red box hit `<Ok>` and press enter
![img](https://images.arsybai.app/images/SilOJuHpHM.png)
it because flask_panel use nginx. so you don't need apache2 and lighttpd

if this appear, just hit yes and input whatever you want.
![img](https://images.arsybai.app/images/tAxLYLNZkd.png)

if the email input appear, just input your email. it's for certbot installation then y,y,y

if the `App running..` apperear, thats mean installation done.
access your panel with flask_panel server_name

Explore it by yourself and feel free to contact me :3
