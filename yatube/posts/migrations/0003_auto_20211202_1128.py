# Generated by Django 2.2.19 on 2021-12-02 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20211202_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.CharField(max_length=50),
        ),
    ]
