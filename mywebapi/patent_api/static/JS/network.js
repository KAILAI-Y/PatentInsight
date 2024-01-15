import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

function getSearchKeywordFromURL() {
  var params = new URLSearchParams(window.location.search)
  return params.get('q')
}

function performNetworkAnalysis() {
  var searchKeyword = getSearchKeywordFromURL()
  var networkChartData = localStorage.getItem('networkChart')
  var base64Images = [networkChartData].filter(Boolean)

  sendMessage(searchKeyword, base64Images, 'network')
}

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket(function () {
    console.log('WebSocket 连接成功，自动执行网络分析')
    document.getElementById('loading').style.display = 'flex'
    // performNetworkAnalysis()
  })

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      performNetworkAnalysis()
    })
})
