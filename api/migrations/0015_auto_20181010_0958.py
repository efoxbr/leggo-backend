# Generated by Django 2.1.2 on 2018-10-10 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20181009_1433'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progresso',
            old_name='proposicao',
            new_name='etapa',
        ),
    ]
