from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0005_aboutsettings_contactsettings_identitysettings_and_more')]

    operations = [
        migrations.DeleteModel(name='AboutSettings'),
        migrations.DeleteModel(name='ContactSettings'),
        migrations.DeleteModel(name='IdentitySettings'),
        migrations.DeleteModel(name='OverviewSettings'),
        migrations.DeleteModel(name='TechStackSettings'),
        migrations.DeleteModel(name='Highlight'),
        migrations.DeleteModel(name='Skill'),
        migrations.RemoveField(model_name='sociallink', name='placement'),
        migrations.AlterField(model_name='siteconfig', name='first_name',
                              field=models.CharField(max_length=80, blank=True)),
        migrations.AlterField(model_name='siteconfig', name='last_name',
                              field=models.CharField(max_length=80, blank=True)),
    ]
