import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket()

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      var searchKeyword = '{{ request.GET.q }}'
      var networkChartData = localStorage.getItem('networkChart')
      var base64Images = [networkChartData].filter(Boolean)

      sendMessage(searchKeyword, base64Images)
    })
})
