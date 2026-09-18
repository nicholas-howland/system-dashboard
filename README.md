# System Dashboard
Very simple system dashboard application for at a glance measuring of current system load and network connections. Pair programmed with Gemini


## Installation

Self signed certificate generation
```bash
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 \
  -keyout system-monitor.key -out system-monitor.crt -days 365 -noenc \
  -subj "/CN=system-monitor.local" \
  -addext "subjectAltName=DNS:localhost,DNS:system-monitor.local,IP:127.0.0.1" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "keyUsage=critical,digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth"
```

Install the virtual environment
```bash
# make sure the virutal environment is installed
apt install python3-venv
# create a new venv
python3 -m venv venv
# activate the venv
source venv/bin/activate
# install the requirements
pip install -r requirements.txt
# deactivate the virtual environment for now...
deactivate
```

## Starting the Server
This will start the server on port 5000 after activating the virtual environment.
```bash
# activate the virtual environment once again
source venv/bin/activate
# start the applicaiton
python3 ./app.py
```
