from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_menuitem_sub_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='special_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Offer/limited time price. Leave blank to use the normal price.', max_digits=10, null=True, verbose_name='Special Price'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='takeaway_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Price when the item is packed. Leave blank to use the normal price.', max_digits=10, null=True, verbose_name='Takeaway Price'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Normal Price'),
        ),
    ]
