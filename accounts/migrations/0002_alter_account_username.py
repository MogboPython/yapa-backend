# Generated by Django 5.1.5 on 2025-03-31 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='username'),
        ),
    ]
