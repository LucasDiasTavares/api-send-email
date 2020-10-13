# Command Reference

# Create virtual environment
    `python3 -m venv nomeDoAmbiente`
    `. nomeDoAmbiente/bin/activate`
    Para desativar so digitar `deactivate` no terminal

# Install requirements
    `pip install -r requirements.txt`
    
# Create required tables
    `python manage.py migrate`
    
# .env example
```
SECRET_KEY=SomeRandomStringd5a4sd3242**kjdfa))h(ljfk)87632&*42%$
DEBUG=True
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_HOST_USER=HostUserEmail
EMAIL_HOST_PASSWORD=HostUserPassword
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

# Max size
```python 
content = CharField(max_length=65535)
emailFrom = EmailField(max_length=256)
emailTo = EmailField(max_length=256)
file = FileField(null=True, blank=True)
```
