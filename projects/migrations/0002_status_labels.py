from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('open', 'Открыт'), ('closed', 'Закрыт')], default='open', max_length=6, verbose_name='Статус'),
        ),
    ]
