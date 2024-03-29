# Generated by Django 5.0rc1 on 2024-01-15 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patent_api', '0005_remove_usersearch_word_network_image_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersearch',
            name='distribution_bar_base64',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersearch',
            name='distribution_line_base64',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersearch',
            name='innovation_bar_base64',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersearch',
            name='innovation_map_base64',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usersearch',
            name='network_base64',
            field=models.TextField(blank=True, null=True),
        ),
    ]
