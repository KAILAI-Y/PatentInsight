function downloadReport() {
  // 收集所有必要的数据
  var distLineChartData = localStorage.getItem('distributionLineChart')
  var distBarChartData = localStorage.getItem('distributionBarChart')
  var conclusionText = localStorage.getItem('conclusionText')

  var reportData = {
    charts: [distLineChartData, distBarChartData /*, 其他图表数据 */],
    text: conclusionText,
    // 包含其他需要的文本或数据
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
