# Generated by Django 2.2.10 on 2020-02-21 02:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0007_merge_preverbs'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='wordform',
            name='API_wordfor_full_lc_50b527_idx',
        ),
        migrations.RemoveIndex(
            model_name='wordform',
            name='API_wordfor_pos_b47c18_idx',
        ),
    ]
