# Generated by Django 2.1.1 on 2018-09-10 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_proposicao_casa_origem'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposicao',
            name='autor_nome',
            field=models.TextField(blank=True),
        ),
    ]
