# ETH Node listener

# Development

```commandline
virtualenv -p python3.6 venv
source venv/bin/activate

$ pip3 install -r requirements.txt

```

## Start gunicorn
если еще не установлен supervisor то
```bash
apt-get install supervisor
```
скопировать в /etc/supervisor/conf.d/
конфиг extra/gunicorn/eth_node_listener.conf

команды для supervisor
```bash
supervisorctl reread
supervisorctl update
supervisorctl status eth_node_listener
supervisorctl restart eth_node_listener
```
проверка
ps xa | grep gunicorn