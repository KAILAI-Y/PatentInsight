import { initializeWebSocket, sendMessage } from './gpt-websocket.js'

// 定义一个函数来处理分析逻辑
function performInnovationAnalysis() {
  var searchKeyword = '{{ request.GET.q }}'
  var innovationBarChartData = localStorage.getItem('innovationBarChart')
  var innovationMapChartData = localStorage.getItem('innovationMapChart')
  var base64Images = [innovationBarChartData, innovationMapChartData].filter(
    Boolean
  )

  sendMessage(searchKeyword, base64Images)
}

document.addEventListener('DOMContentLoaded', function () {
  initializeWebSocket(function () {
    console.log('WebSocket 连接成功，自动执行分析')
    document.getElementById('loading').style.display = 'flex'
    // performInnovationAnalysis()
  })

  document
    .getElementById('conclusion-analyze-button')
    .addEventListener('click', function () {
      document.getElementById('loading').style.display = 'flex'
      performInnovationAnalysis()
    })
})
