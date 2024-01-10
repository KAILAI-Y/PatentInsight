import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

function performNetworkAnalysis() {
  var searchKeyword = '{{ request.GET.q }}'
  var networkChartData = localStorage.getItem('networkChart')
  var base64Images = [networkChartData].filter(Boolean)

  console.log(base64Images)
  sendMessage(searchKeyword, base64Images)
}

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket(function () {
    console.log('WebSocket 连接成功，自动执行网络分析')
    document.getElementById('loading').style.display = 'flex'
    performNetworkAnalysis()
  })

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      performNetworkAnalysis()
    })
})
