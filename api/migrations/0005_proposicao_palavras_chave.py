# Generated by Django 2.1.1 on 2018-09-10 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20180905_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposicao',
            name='palavras_chave',
            field=models.TextField(blank=True),
        ),
    ]
