import os, json

with open('config.json', 'r') as cfg:
    config = json.load(cfg)

os.system("sudo apt update -y")
os.system("sudo apt install nginx -y")
os.system("sudo ufw app list")
os.system("sudo ufw allow 'Nginx Full'")

os.system("sudo apt install mysql-server -y")
os.system("sudo apt install php{phpver}-fpm php-mysql -y".format(**config))

try:
    os.system("mysql -u 'root' -e \"create database flask_panel\"")
    os.system("mysql -u 'root' -e \"create user 'fpanel'@'localhost' identified with mysql_native_password by '@Fpanel123'\"")
    os.system("mysql -u 'root' -e \"grant all privileges on flask_panel.* to 'fpanel'@'localhost'\"")
    os.system("mysql -h localhost -u root flask_panel < flask_panel.sql")
except Exception as e:
    print(e)

tt = """
server {
    listen 80;
    server_name """+config['server_name']['flask_panel']+""";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
with open('/etc/nginx/sites-enabled/flask_panel', 'w') as ww:
    ww.write(tt)

os.system("sudo apt install certbot python3-certbot-nginx -y")

try:
    os.system("sudo certbot --nginx -d {flask_panel}".format(**config['server_name']))
except Exception as e:
    print(e)

os.system("sudo pip3 install flask")
os.system("sudo pip3 install waitress")
os.system("sudo systemctl restart nginx")

#==============================================
os.system("sudo apt install phpmyadmin -y")
os.system("sudo mkdir /var/www/database")
os.system("sudo chown -R $USER:$USER /var/www/database")
os.system("sudo ln -s /usr/share/phpmyadmin /var/www/database/phpmyadmin")

tt = """
server {
    listen 80;
    server_name """+config['server_name']['phpmyadmin']+""";
    root /var/www/database;

    index index.html index.htm index.php;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php"""+config['phpver']+"""-fpm.sock;
     }

    location ~ /\.ht {
        deny all;
    }

}
"""
with open('/etc/nginx/sites-available/database', 'w') as ww:
    ww.write(tt)

os.system("sudo ln -s /etc/nginx/sites-available/database /etc/nginx/sites-enabled/")
os.system("sudo systemctl restart nginx")
try:
    os.system("sudo certbot --nginx -d {phpmyadmin}".format(**config['server_name']))
except Exception as e:
    print(e)

os.system("sudo pip3 install pymysql")

os.system("clear")
os.system("python3 flask_panel/main.py")