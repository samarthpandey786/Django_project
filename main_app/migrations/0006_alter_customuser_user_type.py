# Generated by Django 5.1.7 on 2025-04-15 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_studentpayment_course_studentpayment_transaction_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[(1, 'HOD'), (2, 'Staff'), (3, 'Student'), (4, 'library')], default=1, max_length=1),
        ),
    ]
