// Global variables
const selectedTopicId = getTopicIdFromURL();
let questionCount = 0;
let questionIndex = 0;
let progress = 0;
let accuracy = 0.0;

// Function to handle the topic selection
function selectTopic(topicId) {
  fetch('/get_question', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic_id: topicId,
      current_idx: questionIndex
    })
  })
    .then(response => {
      if (response.ok) {
        // Redirect to quiz.html
        window.location.href = `/quiz?topic_id=${topicId}`;
      } else {
        throw new Error('Error:', response.statusText);
      }
    })
    .catch(error => {
      console.error('Error selecting topic:', error);
    });
}

// Function to retrieve the topic ID from the URL
function getTopicIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('topic_id');
}

// Function to retrieve the number of questions for a topic
function getNumberOfQuestions(topicId) {
  fetch('/get_number_of_questions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ topicId })
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Error:', response.statusText);
      }
    })
    .then(data => {
      questionCount = data.number_of_questions;
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Function to update the UI with the next question
function updateQuestionInterface(question) {
  // Update the question and hide explanation
  document.getElementById('question').innerHTML = question.question_html;
  document.getElementById('result').style.display = 'none';
  document.getElementById('explanation').style.display = 'none';
  document.getElementById('nextButton').style.display = 'none';

  // Ensure options are enabled
  const ul = document.getElementById('answer_choices');
  ul.querySelectorAll('li').forEach(function (li) {
    li.style.pointerEvents = 'auto';
  });

  // Show the selected topic
  document.getElementById('topic-name').innerHTML = question.topic_name;

  // Update progress tracker
  var progressTracker = document.getElementById('progress-tracker');
  progressTracker.innerHTML = `Question: ${questionIndex + 1}/${questionCount}`;

  // Call the syntax highlighting after the content is added to the DOM
  setTimeout(() => {
    hljs.highlightAll();
  }, 0);
}

// Function to handle the AJAX success response for checking the answer
function handleAnswerCheckResponse(response, selectedChoice) {
  // Increment the question index
  questionIndex++;

  // Update running accuracy and display the result
  accuracy = (accuracy * (1 - (1 / questionIndex))) +
    (response.is_correct * (1 / questionIndex));
  document.getElementById('accuracy-value').textContent =
    Math.round(accuracy * 100) + '%';

  var resultElement = document.getElementById('result');
  if (response.is_correct) {
    resultElement.textContent = 'Correct!';
    resultElement.classList.remove('alert-danger');
    resultElement.classList.add('alert-success');
  } else {
    resultElement.textContent = 'Incorrect!';
    resultElement.classList.remove('alert-success');
    resultElement.classList.add('alert-danger');
  }
  resultElement.style.display = 'block';

  // Update the progress bar
  progress = Math.round((questionIndex / questionCount) * 100);
  var progressBar = document.getElementById('progress-bar');
  progressBar.style.width = progress + '%';
  progressBar.textContent = progress + '%';

  // Display the explanation and next-page button
  var explanationElement = document.getElementById('explanation');
  explanationElement.innerHTML = response.explanation;
  explanationElement.style.display = 'block';

  var nextButton = document.getElementById('nextButton');
  nextButton.style.display = 'inline-block';

  // If end of the quiz, save results and create a link back to the Homepage
  if (questionIndex === questionCount) {
    saveResults();
    nextButton.textContent = 'Back to Homepage';
    nextButton.removeAttribute('onclick');
    nextButton.setAttribute('href', '/index');
  }

  // Update options to show the correct/incorrect answers
  var ul = document.getElementById('answer_choices');
  var correctChoice = ul.querySelectorAll('li')[response.correct_choice];
  correctChoice.style.borderColor = '#198754';
  if (response.correct_choice !== selectedChoice) {
    var selectedChoiceElement = ul.querySelectorAll('li')[selectedChoice];
    selectedChoiceElement.style.borderColor = '#dc3545';
  }

  // Disable the possible answer options
  var listItems = ul.querySelectorAll('li');
  for (var i = 0; i < listItems.length; i++) {
    listItems[i].style.pointerEvents = 'none';
  }

  // Call the syntax highlighting after the content is added to the DOM
  setTimeout(function () {
    hljs.highlightAll();
  }, 0);
}

// Function to retrieve the next question using AJAX
function getNextQuestion() {
  fetch('/get_question', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic_id: selectedTopicId,
      current_idx: questionIndex
    })
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Error:' + response.status);
      }
    })
    .then(response => {
      updateQuestionInterface(response);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Function to check the selected answer using AJAX
function checkAnswer(selectedChoice) {
  fetch('/check_answer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      current_idx: questionIndex,
      selected_choice: selectedChoice
    })
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Error:' + response.status);
      }
    })
    .then(response => {
      handleAnswerCheckResponse(response, selectedChoice);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Function to save the quiz results
function saveResults() {
  fetch('/save_results', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      topic_id: selectedTopicId,
      accuracy: accuracy
    })
  })
    .catch(error => {
      console.error('Error:', error);
    });
}

// Function to start the quiz
function startQuiz() {
  if (selectedTopicId) {
    console.log('Starting quiz for topic ID:', selectedTopicId);
    questionCount = getNumberOfQuestions(selectedTopicId);
    getNextQuestion();
  }
}
