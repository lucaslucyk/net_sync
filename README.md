# net_sync
syncs for spec and third software

#### If you use SPECManager connection on linux, install system dependencies before installing:
1. Install dependencies
```bash
sudo apt-get install unixodbc-dev freetds-dev freetds-bin tdsodbc
```

3. In the application, use "connector" key with `/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so` how value in your credential parameters.
