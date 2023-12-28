var socket

document.addEventListener('DOMContentLoaded', function () {
  socket = new WebSocket('ws://' + window.location.host + '/ws/gpt/')

  socket.onopen = function (e) {
    console.log('WebSocket 连接成功')
  }

  socket.onmessage = function (e) {
    var data = JSON.parse(e.data)
    // console.log('Received WebSocket message: ', data)
    var message = data.message
    document.getElementById('write-area').innerHTML += message
    // document.getElementById('write-area').innerHTML = ''
    // typeWriter(message, 'write-area')
  }

  socket.onclose = function (e) {
    console.error('WebSocket 连接意外关闭')
  }
})

// function typeWriter(text, elementId, speed = 50) {
//   console.log('typeWriter called with text: ' + text)
//   let i = 0
//   function typing() {
//     if (i < text.length) {
//       console.log('Adding character: ' + text.charAt(i))
//       document.getElementById(elementId).innerHTML += text.charAt(i)
//       i++
//       setTimeout(typing, speed)
//     }
//   }
//   typing()
// }
