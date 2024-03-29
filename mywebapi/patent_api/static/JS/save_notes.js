function editConclusion() {
  const conclusion = document.querySelector('.conclusion')
  const comments = document.querySelector('#comments')
  const writeArea = document.querySelector('#write-area')
  const saveButton = document.querySelector('#save-button')

  writeArea.style.minHeight = '100px'
  conclusion.onclick = function (event) {
    comments.style.display = 'none'
    event.stopPropagation()
    saveButton.style.display = 'block'
  }

  document.onclick = function () {
    saveButton.style.display = 'none'
  }
}

function saveUserNotes() {
  var content = document.getElementById('write-area').innerHTML
  var searchKeyword = getSearchKeyword()
  var analysisType = getAnalysisType()

  fetch('/save_notes/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify({
      content: content,
      searchKeyword: searchKeyword,
      analysisType: analysisType,
    }),
  }).then((response) => {
    if (response.ok) {
      alert('注释已保存')
    } else {
      alert('保存失败')
    }
  })
}

function getCSRFToken() {
  var cookies = document.cookie.split(';')
  for (var i = 0; i < cookies.length; i++) {
    var cookie = cookies[i].trim()
    if (cookie.startsWith('csrftoken=')) {
      return cookie.substring('csrftoken='.length, cookie.length)
    }
  }
  return ''
}

function getAnalysisType() {
  var path = window.location.pathname
  var segments = path.split('/')
  var analysisType = segments.length > 1 ? segments[1] : ''
  return analysisType
}

function getSearchKeyword() {
  var params = new URLSearchParams(window.location.search)
  return params.get('q')
}
