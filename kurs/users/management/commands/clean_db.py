from django.core.management.base import BaseCommand
import os
import shutil

class Command(BaseCommand):
    help = 'Clean database and migrations'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # Remove db
        db_path = os.path.join(base_dir, 'db.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS('Database removed'))
        
        # Remove migrations
        for app in ['products', 'users']:
            migrations_dir = os.path.join(base_dir, app, 'migrations')
            if os.path.exists(migrations_dir):
                shutil.rmtree(migrations_dir)
                self.stdout.write(self.style.SUCCESS(f'{app} migrations removed'))
        
        self.stdout.write(self.style.SUCCESS('Clean complete!'))