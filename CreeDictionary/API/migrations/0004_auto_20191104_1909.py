# Generated by Django 2.2.6 on 2019-11-04 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("API", "0003_dictionarysource")]

    operations = [
        migrations.AddField(
            model_name="definition",
            name="citations",
            field=models.ManyToManyField(to="API.DictionarySource"),
        ),
        migrations.AlterField(
            model_name="dictionarysource",
            name="year",
            field=models.IntegerField(
                blank=True,
                help_text="What year was this dictionary published?",
                null=True,
            ),
        ),
    ]
