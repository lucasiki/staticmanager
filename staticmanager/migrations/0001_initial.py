# Generated by Django 3.2.13 on 2022-06-13 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='staticManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyobj', models.CharField(max_length=255, unique=True)),
                ('type', models.IntegerField(default=1)),
                ('textobj', models.CharField(default='', max_length=255)),
                ('textareaobj', models.TextField(default='')),
                ('fileobj', models.CharField(default='', max_length=255)),
            ],
        ),
    ]
