# Generated data migration to add default categories

from django.db import migrations


def add_default_categories(apps, schema_editor):
    Category = apps.get_model('projects', 'Category')
    categories = [
        'Web Development',
        'Android',
        'AI/ML',
        'Data Science',
        'IoT',
        'Game Development',
        'Desktop Application',
        'Cloud Computing',
    ]
    
    for category_name in categories:
        Category.objects.get_or_create(name=category_name)


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('projects', 'Category')
    categories = [
        'Web Development',
        'Android',
        'AI/ML',
        'Data Science',
        'IoT',
        'Game Development',
        'Desktop Application',
        'Cloud Computing',
    ]
    
    for category_name in categories:
        Category.objects.filter(name=category_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_project_project_link_project_roll_number_and_more"),
    ]

    operations = [
        migrations.RunPython(add_default_categories, remove_default_categories),
    ]
