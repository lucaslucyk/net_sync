# net_sync
syncs for spec and third software

#### If you use SPECManager connection on linux, follow these steps before installing:
1. Install dependencies
```bash
sudo apt-get install unixodbc-dev freetds-dev freetds-bin tdsodbc
```

2. Edit as root -we create if it does not exist- the file /etc/odbc.ini
```bash
sudo nano /etc/odbc.ini
```

```
[FreeTDS]
Description=FreeTDS Driver
Driver=/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so
Setup=/usr/lib/x86_64-linux-gnu/odbc/libtdsS.so
```

3. Save file and use the key "connector" with value FreeTDS in sync configuration.

