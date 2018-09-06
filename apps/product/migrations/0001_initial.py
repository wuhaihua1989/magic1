# Generated by Django 2.0.7 on 2018-09-05 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_at', models.DateField(auto_now=True, verbose_name='更新时间')),
                ('appearance', models.CharField(blank=True, max_length=266, null=True, verbose_name='外观')),
                ('factory', models.CharField(blank=True, max_length=166, null=True, verbose_name='生产加工')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '个性化定制成品',
                'verbose_name_plural': '个性化定制成品',
                'db_table': 'm_custom_product',
            },
        ),
        migrations.CreateModel(
            name='CustomProductElectron',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_at', models.DateField(auto_now=True, verbose_name='更新时间')),
                ('model_name', models.CharField(max_length=366, null=True, verbose_name='模型名称')),
                ('is_record', models.BooleanField(default=False, verbose_name='是否收录')),
                ('is_key', models.BooleanField(default=False, verbose_name='是否是主要器件')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '个性化成品器件',
                'verbose_name_plural': '个性化成品器件',
                'db_table': 'm_custom_product_electron',
            },
        ),
        migrations.CreateModel(
            name='CustomProductScheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_at', models.DateField(auto_now=True, verbose_name='更新时间')),
                ('scheme_name', models.CharField(blank=True, max_length=366, null=True, verbose_name='方案名称')),
                ('is_record', models.BooleanField(default=False, verbose_name='是否收录')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '个性化成品方案',
                'verbose_name_plural': '个性化成品方案',
                'db_table': 'm_custom_product_scheme',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateField(auto_now_add=True, verbose_name='创建时间')),
                ('update_at', models.DateField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(max_length=166, verbose_name='名称')),
                ('price', models.FloatField(blank=True, verbose_name='价格')),
                ('views', models.IntegerField(blank=True, default=0, null=True, verbose_name='浏览量')),
                ('desc', models.TextField(blank=True, null=True, verbose_name='成品描述')),
                ('source_web', models.CharField(blank=True, max_length=366, null=True, verbose_name='来源站点')),
                ('images', models.TextField(blank=True, null=True, verbose_name='图片地址')),
                ('origin', models.CharField(blank=True, choices=[('1', '国内'), ('0', '国外')], max_length=16, null=True, verbose_name='产地')),
                ('market_date_at', models.DateTimeField(blank=True, null=True, verbose_name='上市时间')),
                ('factory', models.CharField(blank=True, max_length=366, null=True, verbose_name='生产商')),
            ],
            options={
                'verbose_name': '产品',
                'verbose_name_plural': '产品',
                'db_table': 'm_product',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=188, unique=True, verbose_name='类目描述')),
                ('image', models.CharField(blank=True, max_length=366, null=True, verbose_name='类型图片')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='product.ProductCategory')),
            ],
            options={
                'verbose_name': '产品类型',
                'verbose_name_plural': '产品类型',
                'db_table': 'm_product_category',
            },
        ),
        migrations.CreateModel(
            name='ProductElectron',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(blank=True, max_length=366, null=True, verbose_name='描述')),
                ('model_desc', models.CharField(blank=True, max_length=366, null=True, verbose_name='描述')),
                ('is_key', models.BooleanField(default=False, verbose_name='是否是主要器件')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='electrons', to='product.Product', verbose_name='成品')),
            ],
            options={
                'verbose_name': '产品BOM清单',
                'verbose_name_plural': '产品BOM清单',
                'db_table': 'm_product_electron',
            },
        ),
        migrations.CreateModel(
            name='ProductVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateField(auto_now_add=True, verbose_name='创建时间')),
                ('update_at', models.DateField(auto_now=True, verbose_name='更新时间')),
                ('url', models.TextField(blank=True, null=True, verbose_name='视屏地址')),
                ('name', models.CharField(blank=True, max_length=188, null=True, verbose_name='视频名称')),
                ('is_key', models.BooleanField(default=False, verbose_name='是否主视图')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='product.Product', verbose_name='成品')),
            ],
            options={
                'verbose_name': '成品视频',
                'verbose_name_plural': '成品视频',
                'db_table': 'm_product_video',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.ProductCategory', verbose_name='类型'),
        ),
    ]
