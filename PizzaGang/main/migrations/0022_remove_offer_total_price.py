# Generated by Django 4.1.7 on 2023-08-08 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_remove_pizza_duplication_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='total_price',
        ),
    ]
