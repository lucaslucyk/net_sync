# net_sync
syncs for spec and third software

#### If you use SPECManager (with MSSQL) connection on linux, install system dependencies before installing:
1. Install system dependencies
```bash
user@PC:~$ sudo apt-get install unixodbc-dev freetds-dev freetds-bin tdsodbc
```

2. Install app dependencies
```bash
user@PC:~$ cd /etc/
user@PC:/etc/$ git clone https://github.com/lucaslucyk/net_sync.git
user@PC:/etc/$ cd net_sync/src
user@PC:/etc/net_sync/src$ python -m pip install -r requirements.txt
```

3. Make migrations and migrate [-sync database-]
```bash
user@PC:/etc/net_sync/src$ python manage.py makemigrations
user@PC:/etc/net_sync/src$ python manage.py migrate
user@PC:/etc/net_sync/src$ python manage.py --run-syncdb
```

4. ** If is the first time, create superuser
```bash
user@PC:/etc/net_sync/src$ python manage.py createsuperuser
```

5. Run server
```bash
user@PC:/etc/net_sync/src$ python manage.py runserver
```

6. In the application, use "connector" key with `/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so` how value in your credential parameters.
