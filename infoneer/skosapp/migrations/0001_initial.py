# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-06 02:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RdfUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('owner', models.CharField(default='public', max_length=64)),
                ('rdf_file', models.FileField(upload_to='rdfs/', verbose_name='File')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
