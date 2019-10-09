# Generated by Django 2.2.5 on 2019-09-27 16:13

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0030_auto_20190920_0424'),
        ('carbon_calculator', '0003_auto_20190925_2134'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('helptext', models.CharField(blank=True, max_length=10000)),
                ('average_points', models.PositiveIntegerField(default=0)),
                ('questions', django.contrib.postgres.fields.jsonb.JSONField(blank=True)),
                ('picture', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cc_action_picture', to='database.Media')),
            ],
            options={
                'db_table': 'cc_action',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('shortname', models.CharField(max_length=15, null=True)),
                ('datetime', models.DateTimeField()),
                ('location', models.CharField(blank=True, max_length=100)),
                ('host_org', models.CharField(blank=True, max_length=100)),
                ('host_contact', models.CharField(blank=True, max_length=100)),
                ('host_email', models.EmailField(max_length=254)),
                ('host_phone', models.CharField(blank=True, max_length=15)),
                ('host_url', models.URLField(blank=True)),
                ('sponsor_org', models.CharField(blank=True, max_length=100)),
                ('sponsor_url', models.URLField(blank=True)),
                ('host_logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_host_logo', to='database.Media')),
                ('sponsor_logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_sponsor_logo', to='database.Media')),
            ],
            options={
                'db_table': 'cc_event',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('question_text', models.CharField(max_length=100)),
                ('question_type', models.CharField(choices=[('C', 'Choice'), ('T', 'Text'), ('N', 'Number')], default='C', max_length=15)),
                ('response_1', models.CharField(max_length=100, null=True)),
                ('skip_1', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('response_2', models.CharField(max_length=100, null=True)),
                ('skip_2', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('response_3', models.CharField(max_length=100, null=True)),
                ('skip_3', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('response_4', models.CharField(max_length=100, null=True)),
                ('skip_4', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('response_5', models.CharField(max_length=100, null=True)),
                ('skip_5', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('response_6', models.CharField(max_length=100, null=True)),
                ('skip_6', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cc_question',
            },
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=25, unique=True)),
                ('description', models.CharField(max_length=100)),
                ('actions', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'cc_station',
            },
        ),
        migrations.RemoveField(
            model_name='ccactionpoints',
            name='action',
        ),
        migrations.RemoveField(
            model_name='ccactionpoints',
            name='user_id',
        ),
        migrations.RemoveField(
            model_name='ccevent',
            name='host_logo',
        ),
        migrations.RemoveField(
            model_name='ccevent',
            name='sponsor_logo',
        ),
        migrations.RemoveField(
            model_name='ccevent',
            name='stations',
        ),
        migrations.DeleteModel(
            name='CCQuestion',
        ),
        migrations.DeleteModel(
            name='CCAction',
        ),
        migrations.DeleteModel(
            name='CCActionPoints',
        ),
        migrations.DeleteModel(
            name='CCEvent',
        ),
        migrations.DeleteModel(
            name='CCStation',
        ),
        migrations.AddField(
            model_name='event',
            name='stations',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cc_station_picture', to='carbon_calculator.Station'),
        ),
    ]