// This file contains the code to display the bar-chart on the history page.


// Populate the dropdown menu with values and set the default value
function populateDropdown(minValue, maxValue, defaultValue) {
  var dropdownMenu = document.getElementById('maxItemsDropdownMenu');

  // Iterate over the range of values to populate the dropdown menu
  for (var i = minValue; i <= maxValue; i++) {
    var listItem = document.createElement('li');
    listItem.classList.add('dropdown-list-item');
    var anchor = document.createElement('a');
    anchor.classList.add('dropdown-item');
    anchor.href = '#';
    anchor.innerHTML = i;

    // Highlight the dropdown item with the default value
    if (i === defaultValue) {
      anchor.classList.add('active');
    }

    // Add a click event listener to update the active class on click
    anchor.addEventListener('click', function () {
      // Remove the active class from all dropdown items
      var dropdownItems = document.getElementsByClassName('dropdown-item');
      for (var j = 0; j < dropdownItems.length; j++) {
        dropdownItems[j].classList.remove('active');
      }

      // Add the active class to the clicked item
      this.classList.add('active');

      // Update the chart with the selected value
      maxItems = parseInt(this.innerHTML);
      updateChart();
    });

    listItem.appendChild(anchor);
    dropdownMenu.appendChild(listItem);
  }
}

// Event listener used to display the chart once the page is loaded
document.addEventListener('DOMContentLoaded', function () {
  const url = window.location.href;
  const topicId = url.split('/').pop();
  let chart = null;

  // Fetch the chart data from the server using ajax
  function fetchData(topicId) {
    return fetch('/get_barchart_data/' + topicId)
      .then(response => response.json())
      .catch(error => {
        console.error('Error fetching chart data:', error);
        throw error;
      });
  }

  // Display the chart using the chart.js library
  function displayChart(data) {

    // Use negative index to slice from the end of the array
    var dates = data.dates.slice(-maxItems);
    var accuracies = data.accuracies.slice(-maxItems);

    var ctx = document.getElementById('barChart').getContext('2d');

    // Destroy the existing chart if it exists before creating a new one
    if (chart) {
      chart.destroy();
    }
    // Create a new chart using the chart.js library
    chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dates,
        datasets: [{
          label: 'Accuracy',
          data: accuracies,
          backgroundColor: 'rgba(13, 202, 240, 0.2)',
          borderColor: 'rgba(0, 0, 0, 0.5)',
          borderWidth: 1
        }]
      },
      // Configure the chart options
      options: {
        plugins: {
          legend: {
            display: false,
          },
        },
        responsive: true,
        scales: {
          y: {
            title: {
              display: true,
              text: 'Accuracy',
              color: "#ffffffd9",
              font: {
                size: 16
              }
            },
            beginAtZero: true,
            min: 0,
            max: 1,
            ticks: {
              callback: function (value, index, values) {
                return (value * 100).toFixed(0) + '%';
              },
              color: "#ffffffd9",
            }
          },
          x: {
            ticks: {
              autoSkip: false,
              maxRotation: 45,
              minRotation: 45,
              color: "#ffffffd9",
            }
          }
        }
      }
    });
  }
  function updateChart() {
    fetchData(topicId, maxItems)
      .then(data => {
        displayChart(data);
      })
      .catch(error => {
        // Handle error
        console.error('Error updating chart:', error);
      });
  }

  function toggleDropdownMenu() {
    const dropdownMenu = document.querySelector('.dropdown-menu');
    dropdownMenu.classList.toggle('show');
  }

  function handleDropdownItemClick(event) {
    const dropdownItem = event.target;
    maxItems = parseInt(dropdownItem.textContent);
    populateDropdown(5, 50, maxItems);
    updateChart();
  }

  // Add click event listener to toggle the dropdown menu
  const dropdown = document.querySelector('.dropdown');
  dropdown.addEventListener('click', toggleDropdownMenu);

  // Add click event listener to handle dropdown item click
  const maxItemsDropdownMenu = document.getElementById('maxItemsDropdownMenu');
  maxItemsDropdownMenu.addEventListener('click', handleDropdownItemClick);

  // Set default max items to 10
  var maxItems = 10;

  // Populate dropdown with values from 5 to 50 and set default value
  populateDropdown(5, 50, maxItems);

  // Display the chart
  updateChart();
});
