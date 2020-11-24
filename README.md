# Command Reference

# Install with Docker
`docker-compose up --build`

# Create virtual environment
    `python3 -m venv nomeDoAmbiente`
    `. nomeDoAmbiente/bin/activate`

# Install requirements
    `pip install -r requirements.txt`
    
# Create required tables
    `python manage.py migrate`
    
# .env example
```
SECRET_KEY=SomeRandomStringd5a4sd3242**kjdfa))h(ljfk)87632&*42%$
DEBUG=True
URL_DOMAIN=http://192.168.99.100:8000
```

# Install RabbitMQ (Ubuntu Linux 20.04LTS)
    `sudo apt-get install rabbitmq-server`

# Run RabbitMQ (Ubuntu Linux 20.04LTS)
    `sudo systemctl start rabbitmq-server`

# See if RabbitMQ is working (Ubuntu Linux 20.04LTS)
   `systemctl status rabbitmq-server`

# Run Celery (Ubuntu Linux 20.04LTS)
    `celery -A core worker --loglevel=info`

# Run RabbitMQ (On Windows)
    `C:\Program Files\RabbitMQ Server\rabbitmq_server-3.8.6\sbin\rabbitmq-server.bat`

# Run Celery  (On Windows)
    `celery -A core worker -l info --pool=solo`
    
# Run Flower
    `flower -A core --port=5555`

# Useful commands
## Show message on completion of task
    `logger.info("Sent review email")`

### Windows Work Around
    `C:\venv\lib\site-packages\tornado\platform\asyncio.py`

    ```
    import sys
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    ```

# django-celery-beat
===============================

`celery -A core beat -l INFO  # For deeper logs use DEBUG`
`celery -A core worker -B -l INFO`

You can also embed beat inside the worker by enabling the workers `-B` option

### Database scheduler
`celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler`
===============================

# API Usage

### Email create
#### http://127.0.0.1:8000/sendemail/

Json Example

```json
{
     "subject": "Bulk Create with nested child",
     "content": "<!DOCTYPE html>\n<html>\n<body>\n\n<h1>My First Heading</h1>\n<p>My first paragraph.</p>\n\n<div>\n    <a href='http://www.lucas.com'>lucas<a/>\n    <a href=\"https://www.lucas2.com\">lucas<a/>\n    <a href=\"https://lucas3.com\">lucas<a/>\n    <a href=\"http://lucas4.gov.com\">lucas<a/>\n    <a href='http://www.lucas.gov.xxx.xxxx.xxx.xxx.com'>lucas<a/>\n    <a href=\"https://external.asd1230-123.asd_internal.asd.gm-_ail.com\">lucas<a/>\n</div>\n\n</body>\n</html>",
     "emailFrom": "django.test.sender@gmail.com",
     "emailTo": "django.test.sender@gmail.com",
     "urls": []
}
```
If everything goes well:
```json
{
    "taskId": "1b7685e6-69cf-4f3a-b089-0125cfc07559",
    "from": "lucas.django.test.sender@gmail.com",
    "to": "lucas.django.test.sender@gmail.com",
    "status": "PENDING"
}
```

else:
```json
{
    "taskId": null,
    "from": "adsadas@gmail.com",
    "to": "lucas.django.test.sender@gmail.com",
    "message": "Email unauthorized"
}
```
### Email detail
#### http://127.0.0.1:8000/sendemail/1b7685e6-69cf-4f3a-b089-0125cfc07559/

You should see something like that

```json
{
    "id": 12,
    "task_id": "1b7685e6-69cf-4f3a-b089-0125cfc07559",
    "created_at": "2020-11-16T12:28:25.907701-03:00",
    "subject": "Bulk Create with nested child",
    "content": "<!DOCTYPE html>\n<html>\n<body>\n\n<h1>My First Heading</h1>\n<p>My first paragraph.</p>\n\n<div>\n    <a href='http://www.lucas.com'>lucas<a/>\n    <a href=\"https://www.lucas2.com\">lucas<a/>\n    <a href=\"https://lucas3.com\">lucas<a/>\n    <a href=\"http://lucas4.gov.com\">lucas<a/>\n    <a href='http://www.lucas.gov.xxx.xxxx.xxx.xxx.com'>lucas<a/>\n    <a href=\"https://external.asd1230-123.asd_internal.asd.gm-_ail.com\">lucas<a/>\n</div>\n\n</body>\n</html>",
    "emailFrom": "django.test.sender@gmail.com",
    "emailTo": "django.test.sender@gmail.com",
    "file": null,
    "urls": [
        {
            "id": 16,
            "created_at": "2020-11-16T12:28:26.261351-03:00",
            "url_link": "https://www.lucas.nested.child.com.br",
            "user_clicked_link": "False",
            "url_linkEmail": 12
        },
        {
            "id": 15,
            "created_at": "2020-11-16T12:28:26.128382-03:00",
            "url_link": "https://www.maybework.lucas.nested.child.com.br",
            "user_clicked_link": "False",
            "url_linkEmail": 12
        },
        {
            "id": 14,
            "created_at": "2020-11-16T12:28:26.018244-03:00",
            "url_link": "https://www.pleasework.lucas.nested.child.com.br",
            "user_clicked_link": "False",
            "url_linkEmail": 12
        }
    ]
}
```

### Email check user openned email
#### http://127.0.0.1:8000/sendemail/pixel/

List with all emails, check `"user_openned_email": "False"` or `"user_openned_email": "True"`

```json
[
    {
        "id": 2,
        "created_at": "2020-11-11T14:46:30.029772-03:00",
        "updated_at": "2020-11-11T14:46:30.029835-03:00",
        "task_id": "dbe3a3ed-c7c4-4824-97e1-2ece8fd52da0",
        "subject": "Regex",
        "content": "<!DOCTYPE html>\n<html>\n<body>\n\n<h1>My First Heading</h1>\n<p>My first paragraph.</p>\n\n<div>\n    <a href='http://www.lucas.com'>lucas<a/>\n    <a href=\"https://www.lucas2.com\">lucas<a/>\n    <a href=\"https://lucas3.com\">lucas<a/>\n    <a href=\"http://lucas4.gov.com\">lucas<a/>\n    <a href='http://www.lucas.gov.xxx.xxxx.xxx.xxx.com'>lucas<a/>\n    <a href=\"https://external.asd1230-123.asd_internal.asd.gm-_ail.com\">lucas<a/>\n</div>\n\n</body>\n</html>",
        "emailFrom": "django.test.sender@gmail.com",
        "emailTo": "django.test.sender@gmail.com",
        "file": null,
        "user_openned_email": "False"
    },
    {
        "id": 1,
        "created_at": "2020-11-11T12:45:24.940981-03:00",
        "updated_at": "2020-11-11T15:02:53.601140-03:00",
        "task_id": "ff001ec5-ea03-466d-86be-65c7350c6a81",
        "subject": "Regex",
        "content": "<!DOCTYPE html>\n<html>\n<body>\n\n<h1>My First Heading</h1>\n<p>My first paragraph.</p>\n\n<div>\n    <a href='http://www.lucas.com'>lucas<a/>\n    <a href=\"https://www.lucas2.com\">lucas<a/>\n    <a href=\"https://lucas3.com\">lucas<a/>\n    <a href=\"http://lucas4.gov.com\">lucas<a/>\n    <a href='http://www.lucas.gov.xxx.xxxx.xxx.xxx.com'>lucas<a/>\n    <a href=\"https://external.asd1230-123.asd_internal.asd.gm-_ail.com\">lucas<a/>\n</div>\n\n</body>\n</html>",
        "emailFrom": "lucas.django.test.sender@gmail.com",
        "emailTo": "lucas.django.test.sender@gmail.com",
        "file": null,
        "user_openned_email": "True"
    }
]
```
