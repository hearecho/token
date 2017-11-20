# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-20 17:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0002_message'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['-pub_time'], 'verbose_name': '留言', 'verbose_name_plural': '留言'},
        ),
        migrations.AddField(
            model_name='message',
            name='sign',
            field=models.CharField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='pub_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]