# Generated by Django 5.0.4 on 2024-05-05 05:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_orderitem_product_orderitem_cartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='cartitem',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='app.product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='app.order'),
        ),
    ]
