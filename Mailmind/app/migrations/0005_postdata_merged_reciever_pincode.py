# Generated by Django 5.1.4 on 2024-12-12 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_postdata_image2'),
    ]

    operations = [
        migrations.AddField(
            model_name='postdata',
            name='merged_reciever_pincode',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
