# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-24 01:01
from __future__ import unicode_literals

from django.db import migrations, models
import form_document.models
import storages.backends.gs


class Migration(migrations.Migration):

    dependencies = [
        ('form_document', '0009_formdocument_access_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='formdocumentasset',
            name='cached_image_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='formdocumentasset',
            name='cached_image_width',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='formdocumentasset',
            name='image',
            field=models.ImageField(height_field='cached_image_height', storage=storages.backends.gs.GSBotoStorage(acl='private', bucket='emondo-documents', querystring_auth=True, querystring_expire=600), upload_to=form_document.models.original_document_path, width_field='cached_image_width'),
        ),
    ]
