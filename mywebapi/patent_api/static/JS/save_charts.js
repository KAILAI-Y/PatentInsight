function saveChartData(chartId, chartInstance) {
  chartInstance.on('finished', function () {
    var imageData = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })

    localStorage.setItem(chartId, imageData)

    sendChartBase64ToBackend(chartId, imageData)
  })
}

function sendChartBase64ToBackend(chartId, base64Data) {
  var searchKeyword = getSearchKeyword()
  fetch('/save_charts/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({
      chartId: chartId,
      base64Data: base64Data,
      searchKeyword: searchKeyword,
    }),
  })
    .then((response) => response.json())
    .then((data) => console.log(data))
    .catch((error) => console.error('Error:', error))
}

function getSearchKeyword() {
  var params = new URLSearchParams(window.location.search)
  return params.get('q')
}
