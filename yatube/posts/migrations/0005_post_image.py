# Generated by Django 2.2.16 on 2022-11-01 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20221101_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True, upload_to='posts/', verbose_name='Картинка'
            ),
        ),
    ]