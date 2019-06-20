# Generated by Django 2.2 on 2019-04-14 20:55

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('database', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age_acknowledgment', models.BooleanField()),
                ('other_info', django.contrib.postgres.fields.jsonb.JSONField()),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.RealEstateUnit')),
                ('community', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='database.Community')),
                ('goals', models.ManyToManyField(to='database.Goal')),
                ('user_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='eventuserrel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.UserProfile'),
        ),
        migrations.AlterField(
            model_name='team',
            name='admins',
            field=models.ManyToManyField(related_name='team_admins', to='database.UserProfile'),
        ),
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(related_name='team_members', to='database.UserProfile'),
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]