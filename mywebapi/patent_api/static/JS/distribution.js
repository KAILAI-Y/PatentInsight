import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

// 定义一个函数来处理分析逻辑
function performDistributionAnalysis() {
  var searchKeyword = '{{ request.GET.q }}'
  var distributionLineChartData = localStorage.getItem('distributionLineChart')
  var distributionBarChartData = localStorage.getItem('distributionBarChart')
  var base64Images = [
    distributionLineChartData,
    distributionBarChartData,
  ].filter(Boolean)

  sendMessage(searchKeyword, base64Images)
}

document.addEventListener('DOMContentLoaded', function () {
  // 初始化WebSocket，并传入一个回调函数
  initializeWebSocket(function () {
    // WebSocket连接成功后的回调，执行分析逻辑
    console.log('WebSocket 连接成功，自动执行分析')
    document.getElementById('loading').style.display = 'flex'
    // performDistributionAnalysis()
  })

  // 绑定按钮点击事件到相同的分析逻辑
  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      performDistributionAnalysis()
    })
})
