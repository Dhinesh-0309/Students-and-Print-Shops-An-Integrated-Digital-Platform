# Generated by Django 5.1.2 on 2024-11-05 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printrequest',
            name='pages',
            field=models.IntegerField(),
        ),
    ]