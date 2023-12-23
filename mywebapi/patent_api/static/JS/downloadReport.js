function saveChartData(chartId, chartInstance) {
  chartInstance.on('finished', function () {
    var imageData = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })

    localStorage.setItem(chartId, imageData)
  })
}

function downloadReport() {
  var distributionlineChartData = localStorage.getItem('distributionLineChart')
  var distributionbarChartData = localStorage.getItem('distributionBarChart')
  var titleText1 = localStorage.getItem('titleText1')
  var titleText2 = localStorage.getItem('titleText2')
  var distributionText = localStorage.getItem('distributionText')

  var innovationBarChartData = localStorage.getItem('innovationBarChart')
  var innovationMapChartData = localStorage.getItem('innovationMapChart')
  var titleText3 = localStorage.getItem('titleText3')
  var titleText4 = localStorage.getItem('titleText4')
  var innovationText = localStorage.getItem('innovationText')

  var networkData = localStorage.getItem('networkChart')
  var titleText5 = localStorage.getItem('titleText5')
  var networkText = localStorage.getItem('networkText')

  var reportData = {
    charts: [
      { title: titleText1, imageData: distributionlineChartData },
      { title: titleText2, imageData: distributionbarChartData },
      // { title: titleText3, imageData: innovationBarChartData },
      // { title: titleText4, imageData: innovationMapChartData },
      { title: titleText5, imageData: networkData },
    ],
    text: distributionText + '\n' + innovationText + '\n' + networkText,
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
