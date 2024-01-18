function editConclusion() {
  const conclusion = document.querySelector('.conclusion')
  const comments = document.querySelector('#comments')
  const writeArea = document.querySelector('#write-area')
  const saveButton = document.querySelector('#save-button')

  writeArea.style.minHeight = '100px'
  conclusion.onclick = function (event) {
    comments.style.display = 'none'
    event.stopPropagation()
    saveButton.style.display = 'block'
  }

  document.onclick = function () {
    saveButton.style.display = 'none'
  }
}

function getChartData() {
  return {
    distributionLineChart: localStorage.getItem('distributionLineChart'),
    distributionBarChart: localStorage.getItem('distributionBarChart'),
    titleText1: localStorage.getItem('titleText1'),
    titleText2: localStorage.getItem('titleText2'),
    distributionText: localStorage.getItem('distributionText'),
    innovationBarChart: localStorage.getItem('innovationBarChart'),
    innovationMapChart: localStorage.getItem('innovationMapChart'),
    titleText3: localStorage.getItem('titleText3'),
    titleText4: localStorage.getItem('titleText4'),
    innovationText: localStorage.getItem('innovationText'),
    networkChart: localStorage.getItem('networkChart'),
    titleText5: localStorage.getItem('titleText5'),
    networkText: localStorage.getItem('networkText'),
    titleText6: localStorage.getItem('titleText6'),
    wordcloudImage: localStorage.getItem('wordcloud'),
  }
}

function downloadReport() {
  var chartData = getChartData()

  var reportData = {
    charts: [
      {
        title: chartData.titleText1,
        imageData: chartData.distributionlineChartData,
      },
      {
        title: chartData.titleText2,
        imageData: chartData.distributionbarChartData,
      },
      {
        title: chartData.titleText3,
        imageData: chartData.innovationBarChartData,
      },
      {
        title: chartData.titleText4,
        imageData: chartData.innovationMapChartData,
      },
      { title: chartData.titleText5, imageData: chartData.networkChartData },
    ],
    text:
      chartData.distributionText +
      '\n' +
      chartData.innovationText +
      '\n' +
      chartData.networkText,
  }

  fetch('/generate_pdf/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify(reportData),
  })
    .then((response) => {
      if (response.ok) {
        return response.blob()
      }
      throw new Error('Network response was not ok.')
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'report.pdf'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
    })
    .catch((error) => {
      console.error('Error:', error)
    })
}

function getCSRFToken() {
  let cookieValue = null
  let name = 'csrftoken'
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
