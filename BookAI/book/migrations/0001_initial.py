# Generated by Django 3.2.11 on 2023-05-30 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buttons', models.TextField(blank=True, null=True)),
                ('imageUrl', models.TextField(blank=True, null=True)),
                ('buttonMessageId', models.TextField(blank=True, null=True)),
                ('originatingMessageId', models.TextField(blank=True, null=True)),
                ('content', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
