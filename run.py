import argparse
import os
import subprocess

from app import app
from utils import populate_database, remove_table_rows


def submodule_update(force=False):
    """
    Update the submodule data repository and populate the database.
    
    Args:
        force (bool, optional): Force update the submodule. Defaults to False.
    """
    if not force:
        # Check if there are differences in the submodule repository
        submodule_status_process = subprocess.run(
            ['git', 'submodule', 'status'],
            capture_output=True
        )
        submodule_status_out = submodule_status_process.stdout.decode().strip()
        if not submodule_status_out.startswith('-'):
            # No differences, exit the function
            print('No differences in the submodule data repository')
            return

    # Update the submodule
    print('Updating the submodule data repository...')
    if force:
        subprocess.run(['git', 'submodule', 'update', '--init', '--force'])
    else:
        subprocess.run(['git', 'submodule', 'update', '--init'])
    # Remove the old data from the database (keeping performance_tracker)
    remove_table_rows('app.db', 'topic')
    remove_table_rows('app.db', 'question')
    # Populate the database with the data from the data directory
    print('Populating the database...')
    populate_database()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SkillsAssist Quiz App')
    parser.add_argument('--clone',
                        action='store_true',
                        help='Clone the data repository')
    parser.add_argument('--force-clone',
                        action='store_true',
                        help='Force clone the data repository')
    args = parser.parse_args()
    if args.clone:
        submodule_update()
    elif args.force_clone:
        submodule_update(force=True)

    # Check if data directory exists before running the app
    if not os.path.exists('app/static/data'):
        # use gitmodules to clone the data repo
        print('Cloning the data repository...')
        subprocess.run([
            'git', 'submodule', 'add',
            'https://github.com/Caff1982/linkedin-skill-assessments-quizzes',
            'app/static/data'])

    # Check if the database exists before running the app
    if not os.path.exists('app.db'):
        print('Populating the database...')
        # Initialise the database
        subprocess.run(['flask', 'db', 'init'])
        subprocess.run(['flask', 'db', 'migrate'])
        subprocess.run(['flask', 'db', 'upgrade'])
        # Populate the database with the data from the data directory
        populate_database()

    # Run the app
    app.run(debug=True)
