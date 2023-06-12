# SkillsAssist

SkillsAssist is a quiz application that uses data from LinkedIn skills assessments. It is designed to help users prepare for interviews or learn new skills. The application is written in Python using Flask and incorporates some JavaScript. SkillsAssist allows users to run the application locally, save their quiz results, and track their progress over time.

## Features

- **LinkedIn Skills Assessments Integration**: SkillsAssist fetches data from LinkedIn skills assessments (from [this](https://github.com/Ebazhanov/linkedin-skill-assessments-quizzes) repository) to provide users with relevant quiz questions. There are 85 available topics which all have multiple choice questions. All duplicated questions and questions without correct answers have been removed to improve the user experience.
- **Local Setup**: SkillsAssist is designed to be run locally, allowing users to have complete control over their quiz experience.
- **Results Tracking**: The application saves users' quiz results, enabling them to track their progress and review their performance.

## LinkedIn Skills Assessments Data

SkillsAssist uses data from LinkedIn Skills Assessments to provide users with relevant quiz questions. LinkedIn Skills Assessments are a collection of multiple-choice quizes designed to evaluate and validate individuals' skills in various areas. More information can be found [here](https://www.linkedin.com/help/linkedin/answer/a507663/linkedin-skill-assessments?lang=en) 

The quiz questions in SkillsAssist are sourced from [this](https://github.com/Ebazhanov/linkedin-skill-assessments-quizzes) repository. I have created a fork ([here](https://github.com/Caff1982/linkedin-skill-assessments-quizzes)) to remove duplicate questions, which is cloned to this repository as a git submodule. 

Whether you are preparing for interviews or aiming to improve your skills, SkillsAssist provides a valuable tool to enhance your knowledge in a structured and practical way.

## Installation

To install and set up SkillsAssist on your local machine, follow these steps:

1. Clone the repository: `git clone https://github.com/Caff1982/SkillsAssist.git`
2. Navigate to the project directory: `cd SkillsAssist`
3. Create a virtual environment: `python3 -m venv venv`
4. Activate the virtual environment:
   - On macOS and Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate.bat`
5. Install the required dependencies: `pip install -r requirements.txt`

## Usage

To run SkillsAssist locally, follow these steps:

1. Ensure you are in the project directory and have the virtual environment activated.
2. Start the application: `python run.py`. When the program is first run the data will be downloaded and the database populated automatically. 
3. Open your web browser and go to `http://localhost:5000` to access SkillsAssist.
4. To check for updates to the data repository run `python run.py --clone`, or to force an update run `python run.py --force-clone`.

## Question Sorting Algorithm

SkillsAssist employs an exponentially weighted average score-based sorting algorithm to prioritize quiz questions. This algorithm ensures that questions are sorted based on their dynamically calculated scores, taking into account both recent and historical performance.

The algorithm operates as follows:

1. Each quiz question is initialized with an ema_score of zero.

2. As users attempt questions and provide answers, the algorithm updates the ema_score for each question.

3. The ema_score is calculated using an exponentially weighted average formula, incorporating the user's performance on the question. The formula used is as follows:
`ema_score = EMA_ALPHA * score + (1 - EMA_ALPHA) * ema_score`
Here, EMA_ALPHA represents the weight given to the most recent score (default is 0.5), while (1 - EMA_ALPHA) represents the weight given to the historical scores. The score is 1 if the answer is correct and 0 if incorrect.

4. Questions with lower exponentially weighted average scores are prioritized and presented to users more frequently, allowing users to focus on the most challenging questions and enhance their skills effectively.

This approach ensures that users receive a tailored learning experience, with the algorithm dynamically adapting to their skill levels and providing targeted practice on areas that require improvement.

## License

SkillsAssist is released under the MIT License.
