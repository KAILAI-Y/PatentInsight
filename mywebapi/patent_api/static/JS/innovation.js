import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket()

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      var searchKeyword = '{{ request.GET.q }}'
      var innovationBarChartData = localStorage.getItem('innovationBarChart')
      var innovationBarChartData = localStorage.getItem('innovationMapChart')
      var base64Images = [
        innovationBarChartData,
        innovationBarChartData,
      ].filter(Boolean)

      sendMessage(searchKeyword, base64Images)
    })
})
