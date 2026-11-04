import core.validators
import django.db.models.functions.text
import django.utils.timezone
import users.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=124, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навыки',
                'ordering': ['name'],
                'constraints': [models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_skill_name_ci', violation_error_message='Такой навык уже существует.')],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(error_messages={'unique': 'Пользователь с таким email уже зарегистрирован.'}, max_length=254, unique=True, verbose_name='Email')),
                ('name', models.CharField(max_length=124, verbose_name='Имя')),
                ('surname', models.CharField(max_length=124, verbose_name='Фамилия')),
                ('avatar', models.ImageField(upload_to='avatars/', verbose_name='Аватар')),
                ('phone', models.CharField(blank=True, error_messages={'unique': 'Этот номер телефона уже используется.'}, max_length=12, null=True, unique=True, verbose_name='Телефон')),
                ('github_url', models.URLField(blank=True, validators=[core.validators.validate_github_url], verbose_name='GitHub')),
                ('about', models.TextField(blank=True, max_length=256, verbose_name='О себе')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Администратор')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата регистрации')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('skills', models.ManyToManyField(blank=True, related_name='users', to='users.skill', verbose_name='Навыки')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ['-date_joined', '-id'],
            },
            managers=[
                ('objects', users.managers.UserManager()),
            ],
        ),
    ]
