# Generated by Django 3.2.9 on 2021-12-09 19:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indexer', '0002_alter_document_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='url',
            field=models.TextField(unique=True, validators=[django.core.validators.URLValidator()]),
        ),
    ]
