# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-12 00:18
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('blog', '0003_auto_20160512_0745'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogentry',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
