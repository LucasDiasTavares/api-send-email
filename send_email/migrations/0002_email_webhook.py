# Generated by Django 3.1.2 on 2020-11-26 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('send_email', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='webhook',
            field=models.CharField(blank=True, default='', max_length=256, null=True),
        ),
    ]
