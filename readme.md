# ETH Node listener

# Development

```commandline
virtualenv -p python3.6 venv
source venv/bin/activate

pip3 install -r requirements.txt

```

## Start gunicorn

create systemd config like extra/ethlistener.service

### start service
systemctl start ethlistener.service
