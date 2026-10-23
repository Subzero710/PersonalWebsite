from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0004_siteconfig_first_name_siteconfig_last_name_and_more')]

    operations = [
        migrations.CreateModel(
            name='AboutSettings', fields=[],
            options={'proxy': True, 'verbose_name': 'About', 'verbose_name_plural': 'About'},
            bases=('core.siteconfig',),
        ),
        migrations.CreateModel(
            name='ContactSettings', fields=[],
            options={'proxy': True, 'verbose_name': 'Contact & Links', 'verbose_name_plural': 'Contact & Links'},
            bases=('core.siteconfig',),
        ),
        migrations.CreateModel(
            name='IdentitySettings', fields=[],
            options={'proxy': True, 'verbose_name': 'Identity & Job Matching',
                     'verbose_name_plural': 'Identity & Job Matching'},
            bases=('core.siteconfig',),
        ),
        migrations.CreateModel(
            name='OverviewSettings', fields=[],
            options={'proxy': True, 'verbose_name': 'Overview', 'verbose_name_plural': 'Overview'},
            bases=('core.siteconfig',),
        ),
        migrations.CreateModel(
            name='TechStackSettings', fields=[],
            options={'proxy': True, 'verbose_name': 'Tech Stack', 'verbose_name_plural': 'Tech Stack'},
            bases=('core.siteconfig',),
        ),
        migrations.AddField(
            model_name='siteconfig', name='tech_stack_intro',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sociallink', name='placement',
            field=models.CharField(max_length=12, default='links',
                                   choices=[('connect', "Let's Connect"), ('links', 'Links')]),
        ),
    ]
