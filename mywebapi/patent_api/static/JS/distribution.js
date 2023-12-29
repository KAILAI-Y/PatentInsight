import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket()

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      var searchKeyword = '{{ request.GET.q }}'
      var distributionLineChartData = localStorage.getItem(
        'distributionLineChart'
      )
      var distributionBarChartData = localStorage.getItem(
        'distributionBarChart'
      )
      var base64Images = [
        distributionLineChartData,
        distributionBarChartData,
      ].filter(Boolean)

      sendMessage(searchKeyword, base64Images)
    })
})
