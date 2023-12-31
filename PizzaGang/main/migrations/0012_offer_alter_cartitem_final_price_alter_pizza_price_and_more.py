# Generated by Django 4.1.7 on 2023-07-21 09:35

import PizzaGang.main.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_profile_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('total_price', models.FloatField(default=0.0, validators=[PizzaGang.main.validators.validate_positive])),
                ('final_price', models.FloatField(default=0.0, validators=[PizzaGang.main.validators.validate_positive])),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='final_price',
            field=models.FloatField(default=0.0, validators=[PizzaGang.main.validators.validate_positive]),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='price',
            field=models.FloatField(validators=[PizzaGang.main.validators.validate_positive]),
        ),
        migrations.CreateModel(
            name='OfferItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cart')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.offer')),
            ],
        ),
        migrations.AddField(
            model_name='cartitem',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.offer'),
        ),
    ]
