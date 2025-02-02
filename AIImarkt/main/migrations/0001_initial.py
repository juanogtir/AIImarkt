# Generated by Django 3.1.2 on 2021-01-07 01:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equipo',
            fields=[
                ('idEquipo', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(verbose_name='Equipo')),
                ('valor', models.FloatField(verbose_name='Valor')),
                ('url_escudo', models.URLField(verbose_name='URL del escudo')),
            ],
            options={
                'db_table': 'Equipos',
                'ordering': ('nombre', 'valor', 'idEquipo'),
            },
        ),
        migrations.CreateModel(
            name='Jugador',
            fields=[
                ('idJugador', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(verbose_name='Jugador')),
                ('edad', models.IntegerField(help_text='Debe introducir una edad', verbose_name='Edad')),
                ('altura', models.FloatField(verbose_name='Altura')),
                ('valor', models.FloatField(verbose_name='Valor')),
                ('contrato', models.DateField(verbose_name='Contrato')),
                ('capitan', models.BooleanField()),
                ('foto_jugador', models.URLField(verbose_name='URL de la foto del jugador')),
                ('pie', models.CharField(choices=[(main.models.PieChoice['IZQ'], 'izquierdo'), (main.models.PieChoice['DER'], 'derecho'), (main.models.PieChoice['AMB'], 'ambidiestro'), (main.models.PieChoice['IND'], 'indeterminado')], max_length=3, verbose_name='Pie')),
                ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.equipo')),
            ],
            options={
                'db_table': 'Jugadores',
                'ordering': ('nombre', 'valor', 'idJugador'),
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(verbose_name='Nacionalidad')),
            ],
        ),
        migrations.CreateModel(
            name='PosicionPrincipal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(verbose_name='Posición principal')),
            ],
        ),
        migrations.CreateModel(
            name='PosicionSecundaria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(verbose_name='Posición secundaria')),
            ],
        ),
        migrations.CreateModel(
            name='Profesion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.IntegerField(default=1, verbose_name='Numero de la profesion')),
                ('nombre', models.TextField(verbose_name='Nombre de la profesion')),
            ],
            options={
                'db_table': 'Profesiones',
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numUsuario', models.IntegerField(default=1, null=True, verbose_name='Numero de usuario')),
                ('edad', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('genero', models.CharField(choices=[('F', 'Femenino'), ('M', 'Masculino')], max_length=1)),
                ('zipCode', models.CharField(max_length=8)),
                ('equipo_favorito', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.equipo')),
                ('profesion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.profesion')),
            ],
            options={
                'db_table': 'Usuarios',
                'ordering': ('numUsuario',),
            },
        ),
        migrations.CreateModel(
            name='Puntuacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('jugador', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.jugador')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.usuario')),
            ],
        ),
        migrations.AddField(
            model_name='jugador',
            name='nacionalidades',
            field=models.ManyToManyField(to='main.Pais'),
        ),
        migrations.AddField(
            model_name='jugador',
            name='posicion_principal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='main.posicionprincipal'),
        ),
        migrations.AddField(
            model_name='jugador',
            name='posiciones_secundarias',
            field=models.ManyToManyField(to='main.PosicionSecundaria'),
        ),
    ]
