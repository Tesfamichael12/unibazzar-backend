import csv
from django.core.management.base import BaseCommand
from users.models import University
import os
from django.conf import settings

# Define the path to your CSV file relative to the BASE_DIR
# You might want to place this in a 'data' directory within your project root
# e.g., BASE_DIR / 'data' / 'universities.csv'
DEFAULT_CSV_PATH = os.path.join(settings.BASE_DIR, 'universities.csv') 

class Command(BaseCommand):
    help = 'Loads universities from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv_path', 
            type=str, 
            help='Path to the CSV file containing university names',
            default=DEFAULT_CSV_PATH
        )
        parser.add_argument(
            '--name_column', 
            type=str, 
            help='Name of the column containing university names in the CSV',
            default='university_name' # Default column name
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_path']
        name_column = options['name_column']
        
        self.stdout.write(f"Looking for CSV file at: {csv_file_path}")
        
        if not os.path.exists(csv_file_path):
            self.stderr.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
            self.stdout.write("Please create the CSV file or provide the correct path using --csv_path.")
            # Example of how to create a placeholder CSV if it doesn't exist:
            # try:
            #     os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
            #     with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            #         writer = csv.writer(file)
            #         writer.writerow([name_column]) # Write header
            #         writer.writerow(['Placeholder University 1'])
            #         writer.writerow(['Placeholder University 2'])
            #     self.stdout.write(self.style.SUCCESS(f"Created a placeholder CSV at {csv_file_path} with column '{name_column}'"))
            # except Exception as e:
            #     self.stderr.write(self.style.ERROR(f"Could not create placeholder CSV: {e}"))
            return # Exit if file not found

        count = 0
        created_count = 0
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                if name_column not in reader.fieldnames:
                    self.stderr.write(self.style.ERROR(
                        f"Column '{name_column}' not found in CSV file '{csv_file_path}'."
                    ))
                    self.stdout.write(f"Available columns: {', '.join(reader.fieldnames)}")
                    self.stdout.write(f"Please specify the correct column name using --name_column.")
                    return # Exit if column not found
                    
                for row in reader:
                    university_name = row.get(name_column)
                    if university_name: # Ensure the name is not empty
                        university_name = university_name.strip()
                        obj, created = University.objects.get_or_create(
                            name=university_name
                        )
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f'Successfully created university "{university_name}"'))
                        else:
                             self.stdout.write(f'University "{university_name}" already exists.')
                        count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"Skipping row with empty name in column '{name_column}'."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            return

        self.stdout.write(f"Processed {count} universities.")
        self.stdout.write(self.style.SUCCESS(f'Successfully added {created_count} new universities.')) 