# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-03 00:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_explorer', '0003_auto_20160503_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='afslicenseeentry',
            name='principle_business_address',
            field=models.CharField(max_length=512, null=True),
        ),
    ]