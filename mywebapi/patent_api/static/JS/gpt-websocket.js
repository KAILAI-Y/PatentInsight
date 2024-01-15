var socket

function initializeWebSocket(callback) {
  console.log('Initializing WebSocket...')
  socket = new WebSocket('ws://' + window.location.host + '/ws/gpt/')

  socket.onopen = function (e) {
    console.log('WebSocket 连接成功')
    console.log('正在调用回调函数...')
    if (callback && typeof callback === 'function') {
      callback() // 确保这里调用了回调函数
    } else {
      console.error('回调函数无效或未定义')
    }
  }

  socket.onmessage = function (e) {
    var data = JSON.parse(e.data)
    var message = data.message
    document.getElementById('write-area').innerHTML += message
    // typeWriter(message, 'write-area', 0)
    document.getElementById('loading').style.display = 'none'
    // console.log(message)
  }

  socket.onclose = function (e) {
    console.error('WebSocket 连接意外关闭')
  }
}

function sendMessage(searchKeyword, base64Images, analysisType) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error('WebSocket is not connected')
    return
  }

  socket.send(
    JSON.stringify({
      searchKeyword: searchKeyword,
      base64Images: base64Images,
      analysisType: analysisType,
    })
  )
}

function typeWriter(text, elementId, index, speed = 200) {
  if (index < text.length) {
    document.getElementById(elementId).innerHTML += text.charAt(index)
    index++
    setTimeout(function () {
      typeWriter(text, elementId, index, speed)
    }, speed)
  }
}

// 导出模块的函数
export { initializeWebSocket, sendMessage }
