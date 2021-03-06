# Generated by Django 2.0.7 on 2018-11-23 05:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('electron', '0001_initial'),
        ('scheme', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='scheme',
            field=models.ManyToManyField(related_name='products', to='scheme.Scheme', verbose_name='成品方案'),
        ),
        migrations.AddField(
            model_name='customproductscheme',
            name='custom_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schemes_custom', to='product.CustomProduct', verbose_name='个性化配置成品'),
        ),
        migrations.AddField(
            model_name='customproductscheme',
            name='scheme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_scheme', to='scheme.Scheme', verbose_name='方案'),
        ),
        migrations.AddField(
            model_name='customproductelectron',
            name='custom_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='electrons_custom', to='product.CustomProduct', verbose_name='个性化配置元器件'),
        ),
        migrations.AddField(
            model_name='customproductelectron',
            name='electron',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_electrons', to='electron.Electron', verbose_name='元器件'),
        ),
    ]
