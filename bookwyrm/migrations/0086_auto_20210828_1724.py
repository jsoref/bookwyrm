# Generated by Django 3.2.4 on 2021-08-28 17:24

import bookwyrm.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookwyrm', '0085_user_saved_lists'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='followers_url',
            field=bookwyrm.models.fields.CharField(default='/followers', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(through='bookwyrm.UserFollows', to=settings.AUTH_USER_MODEL),
        ),
    ]
