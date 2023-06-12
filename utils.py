import sqlite3
import re
import os
import itertools

import markdown
from bs4 import BeautifulSoup


def remove_duplicate_ul(string):
    """
    Remove duplicate ul tags from a string.

    This is used for cases where there is a ul tag inside 
    a code block. Only the first "<ul" tag and last "</ul>"
    are kept. Returns the string with all double spaces removed.

    Args:
        string (str): A string containing HTML.
    
    Returns:
        str: A string with duplicate ul tags removed.
    """
    # Remove all but the first occurence of <ul> tag
    count = itertools.count()
    ul_substring = '<ul class="list-group" id="answer_choices">'
    string = re.sub(
        ul_substring,
        lambda x: x.group() if not next(count) else '',
        string
    )
    # Remove all but the last occurence of </ul> tag
    if string.count('</ul>') > 1:
        string = string.replace('</ul>', '', string.count('</ul>') - 1)
    # Check for code block after </ul> tag
    if '</ul><pre>' in string:
        ul_idx = string.index('</ul>')
        string = string.replace('</ul><pre>', '<pre>')
        insert_idx = string[ul_idx:].index('</pre>') + ul_idx + len('</pre>')
        string = string[:insert_idx] + '</ul>' + string[insert_idx:]

    # Return string with all double spaces removed
    return string.replace('  ', ' ')


def parse_md_file(filepath, topic_name):
    """
    Parse a markdown file and return a list of tuples.

    Takes a filepath to a markdown file and returns a list of tuples
    where each tuple represents a question and has the form:

    - quesion_number: The number of the question.
    - question_title: The title of the question (i.e. the question text).
    - question_content: The HTML content of the question.
    - question_explanation: The HTML content of the explanation if it exists.
    - correct_index: The index of the correct answer choice.

    Each question is parsed using BeautifulSoup and stored as html
    so that it can be displayed in the quiz.

    Args:
        filepath (str): The path to the markdown file.
        topic_name (str): The name of the topic.
    
    Returns:
        list: A list of tuples representing the questions.
    """
    questions = []
    with open(filepath, 'r') as f:
        md_text = f.read()

    # Update all image paths to point to static folder
    md_text = md_text.replace('(images/', f'(static/data/{topic_name}/images/')
    # Extensions used to preserve newlines and code blocks
    html = markdown.markdown(md_text, extensions=['nl2br', 'fenced_code'])
    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Iterate through each question block and parse it
    for block in soup.find_all('h4'):
        answer_idx = 0
        correct_index = None
        question_explanation = None
        question_number = re.search(r'\d+', block.text).group()
        question_title = ' '.join(block.text.strip().split()[1:])
        question_content = [question_title]
        # Find the next sibling until the next question block or end of file
        next_sibling = block.next_sibling
        while next_sibling and next_sibling.name != 'h4':
            if next_sibling.name == 'ul':
                # Add the answer choices
                next_sibling['class'] = 'list-group'
                next_sibling['id'] = 'answer_choices'
                answer_choices = []
                for item in next_sibling.find_all('li'):
                    if item.text.strip().startswith('[x]'):
                        correct_index = answer_idx
                    item['onclick'] = f"checkAnswer({answer_idx})"
                    item['class'] = 'my-1 list-group-item'
                    item.string = item.text[4:].strip()
                    answer_choices.append(str(item).strip())
                    # Increment the answer index
                    answer_idx += 1

                question_content.append(str(next_sibling))
            elif next_sibling.name != 'a':
                # Append anchor tags to the question content
                question_content.append(str(next_sibling).strip())
            next_sibling = next_sibling.next_sibling

        question_content_html = ''.join(question_content)
        # Insert 'pre' tag before 'code' tag to enable syntax highlighting
        pattern = r'(<code>.*?</code>)'
        replacement = r'<pre>\1</pre>'
        question_content_html = re.sub(pattern,
                                       replacement,
                                       question_content_html)
        # Remove duplicate ul tags
        question_content_html = remove_duplicate_ul(question_content_html)
        # Check if there is an explanation after the question content
        if not question_content_html.endswith('</ul>'):
            # Split the question content and explanation at list UL tag
            split_idx = question_content_html.index('</ul>') + 5
            question_content, question_explanation = (
                question_content_html[:split_idx],
                question_content_html[split_idx:]
            )
            # Change all <p> tags to <div> in the explanation
            question_explanation = (
                question_explanation
                .replace('<p>', '<div class="my-2">')
                .replace('</p>', '</div>')
            )
            # Change the <strong> tag to <h5> in the explanation
            question_explanation = (
                question_explanation
                .replace('<strong>', '<h5 id="explanation-header">')
                .replace('</strong>', '</h5>')
            )
            # Style anchor tag as button and make link open in new tab
            a_str = '<a target="_blank" id="explanation-header" class="btn btn-secondary"'
            question_explanation = (
                question_explanation
                .replace('<a', a_str)
            )
        else:
            # Question has no explanation, just use the question content
            question_content = question_content_html

        # Remove all p tags from content and append to questions list
        question_content = question_content.replace('<p>', '').replace('</p>', '')
        questions.append((question_number, question_title, question_content,
                          question_explanation, correct_index))

    return questions


def add_topic(topic_name, questions, db_path='app.db'):
    """
    Add a new topic to the database.

    N.B. The database must already exist and have the correct schema.

    Args:
        topic_name (str): The name of the topic.
        questions (list): A list of tuples representing the questions.
        db_path (str, optional): The path to the database file.
                                 Defaults to 'app.db'.
    """
    # Create the databse connection
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Add topic to the database if it doesn't already exist
    try:
        cur.execute("INSERT INTO topic (name) VALUES (?)", (topic_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Topic '{topic_name}' already exists, adding more rows...")
    # Add questions to the database
    topic_id = cur.lastrowid # Get the last inserted row id
    query = """
        INSERT INTO question (
            question_number, question_title, question_html,
            question_explanation, correct_choice, topic_id,
            topic_name, ema_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    for row in questions:
        number, title, content, explanation, correct_idx = row
        # Only add rows that have a correct answer
        if correct_idx is not None:
            cur.execute(query, (number, title, content, explanation,
                                correct_idx, topic_id, topic_name, 0.0))
    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def remove_table_rows(db_path, table_name):
    """Remove all rows from a table in the database."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(f"DELETE from {table_name}")
    conn.commit()
    conn.close()


def populate_database():
    """Populate the database with questions from markdown files."""
    # Iterate over each item in the data directory
    data_dir = 'app/static/data'
    for topic in os.listdir(data_dir):
        path = os.path.join(data_dir, topic)
        # Check if the item is a directory
        if os.path.isdir(path):
            # Ensure the directory contains a markdown file
            try:
                markdown_file = os.path.join(path, f'{topic}-quiz.md')
                questions = parse_md_file(markdown_file, topic)
                add_topic(topic, questions)
            except FileNotFoundError:
                print(f'No markdown file found for {topic}, skipping...')
                