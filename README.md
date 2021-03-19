# net_sync
syncs for spec and third software

#### If you use SPECManager (with MSSQL) connection on linux, install system dependencies before installing:
1. Install system dependencies
```shell
user@PC:~$ sudo apt-get install unixodbc-dev freetds-dev freetds-bin tdsodbc
```

2. Install app dependencies
```shell
user@PC:~$ cd /etc/
user@PC:/etc/$ git clone https://github.com/lucaslucyk/net_sync.git
user@PC:/etc/$ cd net_sync/src
user@PC:/etc/net_sync/src$ python -m pip install -r requirements.txt
```

3. Make migrations and migrate [-sync database-]
```shell
user@PC:/etc/net_sync/src$ python manage.py makemigrations
user@PC:/etc/net_sync/src$ python manage.py migrate
user@PC:/etc/net_sync/src$ python manage.py --run-syncdb
```

4. ** If is the first time, create superuser
```shell
user@PC:/etc/net_sync/src$ python manage.py createsuperuser
```

5. Run server
```shell
user@PC:/etc/net_sync/src$ python manage.py runserver
```

6. In the application, use "connector" key with `/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so` how value in your credential parameters.


## Deploy on Microsoft IIS

- Watch on YouTube: [Deploy Django on Windows using Microsoft IIS](https://youtu.be/APCQ15YqqQ0)

### Steps
1. Install IIS on your VM or machine, and enable CGI

    - [How to Install IIS on Windows 8 or Windows 10](https://www.howtogeek.com/112455/how-to-install-iis-8-on-windows-8/)

    - [CGI](https://docs.microsoft.com/en-us/iis/configuration/system.webserver/cgi)

2. Clone repository in `C:/inetpub/wwwroot/` or create `C:/inetpub/wwwrootns/` if is currently used.

3. Install Python 3.8 (or high) in `C:/Python38`, and install dependences with `requirements/base.txt and requirements/prd-win.txt`.

4. Navigate to `C:/`, right-click on `Python38`, and edit `Properties`.
Under Security, add `IIS AppPool\DefaultAppPool`. `DefaultAppPool` is the default app pool.
** Ensure the location is local and replicate this for `C:/inetpub/wwwroot/net_sync/` directory.

5. Enable wfastcgi

    - Open a CMD terminal as Administrator, change directory with `cd C:\` and run the command `wfastcgi-enable`. 
    
    - Copy the Python path, and replace the `scriptProcessor="<to be filled in>"` in config/iis/web-config-template with the Python path returned by `wfastcgi-enable`.

6. Edit the remaining settings in `web-config-template` then save it as `web.config` in the `C:/inetpub/wwwroot/` directory. It should NOT sit inside `net_sync/`. Other settings can be modified if `net_sync` does NOT sit at `C:/inetpub/wwwroot/`

    - Edit project `PYTHONPATH` (path to your project what includes `manage.py`)

    - Edit `WSGI_HANDLER` (located in your `wsgi.py`)

    - Edit `DJANGO_SETTINGS_MODULE` (your `settings.py` module)

7. Open Internet Information Services (IIS) Manager. Under connections select the server, then in the center pane under Management select Configuration Editor. Under Section select system.webServer/handlers. Under Section select Unlock Section. This is required because the `C:/inetpub/wwwroot/web.config` creates a [route handler](https://pypi.org/project/wfastcgi/#route-handlers) for our project.

8. Run `manage.py collectstatic` for load all staticfiles in `publish/static/` folder.

9. Create folder `publish/media/` and copy `web.config` file from `publish/static/`.

10. Add Virtual Directory. In order to enable serving static files map a static alias to the static directory, `C:/inetpub/wwwroot/net_sync/publish/static/`

11. Add Virtual Directory. In order to enable serving media files map a media alias to the media directory, `C:/inetpub/wwwroot/net_sync/publish/media/`

9. Refresh the server and navigate to `localhost`

## Application Guide
...