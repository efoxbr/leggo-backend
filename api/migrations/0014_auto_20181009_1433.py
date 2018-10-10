# Generated by Django 2.1.2 on 2018-10-09 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20181008_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposicao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('apelido', models.TextField(blank=True)),
                ('tema', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='etapaproposicao',
            options={'ordering': ('data_apresentacao',)},
        ),
        migrations.RemoveField(
            model_name='etapaproposicao',
            name='casa_origem',
        ),
        migrations.AddField(
            model_name='etapaproposicao',
            name='proposicao',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='etapas', to='api.Proposicao'),
        ),
    ]
