#!/bin/bash

# Ubuntu 22.04 LTS: disable the popup "Which service should be restarted ?"
sudo sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf
sudo apt update
sudo apt install -y python3-pip python3-venv
sudo apt-get install -y apache2 libapache2-mod-wsgi-py3

mkdir /home/ubuntu/flaskapp && cd /home/ubuntu/flaskapp
python3 -m venv myenv

# Link to the app directory from the site-root defined in apache’s configuration
sudo ln -sT /home/ubuntu/flaskapp /var/www/html/flaskapp

sudo apt install amazon-ec2-utils
# Get the instance id
ThisInstancId=`ec2-metadata -i` 

sudo apt install authbind
# Configure access to port 80
sudo touch /etc/authbind/byport/80
sudo chmod 777 /etc/authbind/byport/80

source myenv/bin/activate
pip3 install flask

# The flask app
cat > /home/ubuntu/flaskapp/flaskapp.py << EOF
from flask import Flask
app = Flask(__name__)

@app.route('/')
def base():
    return '<h1>Welcome to EC2 instances</h1>'

@app.route('/cluster%s', methods=['GET',])
def get_instance():
    return '<h1>Instance $ThisInstancId is responding now!</h1>'

EOF

# Create a .wsgi file to load the app
cat > /home/ubuntu/flaskapp/flaskapp.wsgi << EOF
import sys
sys.path.insert(0, '/var/www/html/flaskapp')
sys.path.insert(0,"/home/ubuntu/flaskapp/myenv/lib/python3.10/site-packages")

from flaskapp import app as application

EOF

# Enable mod_wsgi
sudo sed -i "/DocumentRoot \/var\/www\/html/r /dev/stdin" /etc/apache2/sites-enabled/000-default.conf <<EOF
	
	WSGIDaemonProcess flaskapp threads=5 python-path=/var/www/html/flaskapp/myenv
	WSGIProcessGroup flaskapp
	WSGIApplicationGroup %%{GLOBAL}
	WSGIScriptAlias /  /var/www/html/flaskapp/flaskapp.wsgi

	<Directory flaskapp>
		Options FollowSymlinks
		AllowOverride  All
		Require all granted
		allow from all
	</Directory>
EOF

export flaskapplication=/home/ubuntu/flaskapp/flaskapp.py
authbind --deep python3 /home/ubuntu/flaskapp/flaskapp.py

sudo chmod -R +x /home/ubuntu/
sudo service apache2 restart