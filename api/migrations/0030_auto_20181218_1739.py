# Generated by Django 2.1.4 on 2018-12-18 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_remove_tramitacaoevent_texto'),
    ]

    operations = [
        migrations.AddField(
            model_name='tramitacaoevent',
            name='local',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tramitacaoevent',
            name='sigla_local',
            field=models.TextField(blank=True),
        ),
    ]
