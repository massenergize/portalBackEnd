# Generated by Django 3.0.5 on 2020-07-12 01:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carbon_calculator', '0006_auto_20200628_0100'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='host_contact',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_email',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_logo',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_phone',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_url',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sponsor_logo',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sponsor_url',
        ),
        migrations.RemoveField(
            model_name='event',
            name='host_org',
        ),
        migrations.RemoveField(
            model_name='event',
            name='sponsor_org',
        ),
        migrations.CreateModel(
            name='Org',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('contact', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('about', models.CharField(blank=True, max_length=1000)),
                ('url', models.URLField(blank=True)),
                ('logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_host_logo', to='carbon_calculator.CarbonCalculatorMedia')),
            ],
            options={
                'db_table': 'organization_cc',
            },
        ),
        migrations.AddField(
            model_name='event',
            name='host_org',
            field=models.ManyToManyField(blank=True, related_name='host_orgs', to='carbon_calculator.Org'),
        ),
        migrations.AddField(
            model_name='event',
            name='sponsor_org',
            field=models.ManyToManyField(blank=True, related_name='sponsor_orgs', to='carbon_calculator.Org'),
        ),
    ]