# System Dashboard
Very simple system dashboard application for at a glance measuring of current system load and network connections. 
- Displays Current system load, top 10 processes, and all of the network connections
- All data is available via JSON data api
- Uses HTTPS for data confidentiality, and http basic auth for authorization

Application pair programmed with Gemini, installation documents and process solidification completed independently.

## Installation



Install the virtual environment
```bash
# create the installation directory
sudo mkdir /opt/system-dashboard/
sudo chown $USER /opt/system-dashboard
cd /opt/system-dashboard
# make sure we have the dependencies installed
sudo apt install python3-venv -y

# grab the repository and rename it
wget https://github.com/nicholas-howland/system-dashboard/archive/refs/heads/main.zip
unzip main.zip
mv system-dashboard-main system-dashboard


# create a new venv, activate it and install the requirements, then deactivate it for now...
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```
Self signed certificate generation
```bash
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout system-dashboard.key -out system-dashboard.crt -days 365 -noenc \
  -subj "/CN=system-dashboard.local" \
  -addext "subjectAltName=DNS:localhost,DNS:system-dashboard.local,IP:127.0.0.1" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "keyUsage=critical,digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth"
```
## Starting the Server
This will start the server on port 5000 over https, if you have errors here its because dependencies were not installed or the tls certificate was not generated. Generate the certificate
```bash
# activate the virtual environment once again and start the applicaiton
source venv/bin/activate
python3 ./app.py
```

## Installing the Server
If you want to make the server persistant at startup, putting it inside of a systemd process can be done like so.
```bash
sed "s/USER/$USER/" system-dashboard.service | sudo tee /etc/systemd/system/system-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable system-dashboard
sudo systemctl start system-dashboard


```



