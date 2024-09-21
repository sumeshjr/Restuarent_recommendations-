# Generated by Django 5.1.1 on 2024-09-20 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.TextField(blank=True, max_length=20, null=True)),
                ('password', models.TextField(blank=True, max_length=20, null=True)),
                ('admin', models.BooleanField(default=False)),
            ],
        ),
    ]
