# Generated by Django 4.1.7 on 2023-07-21 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_offer_image_alter_offer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='in_progress',
            field=models.BooleanField(default=True),
        ),
    ]
