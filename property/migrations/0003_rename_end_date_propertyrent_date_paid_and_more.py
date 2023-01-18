# Generated by Django 4.1.5 on 2023-01-18 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0002_rename_image_propertyimages_file_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='propertyrent',
            old_name='end_date',
            new_name='date_paid',
        ),
        migrations.AddField(
            model_name='propertyrent',
            name='amount_paid',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=13, null=True),
        ),
        migrations.AddField(
            model_name='propertyrent',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='propertyrent',
            name='rent_status',
            field=models.CharField(blank=True, choices=[('paid', 'paid'), ('unpaid', 'unpaid'), ('overdue', 'overdue')], max_length=255, null=True),
        ),
    ]