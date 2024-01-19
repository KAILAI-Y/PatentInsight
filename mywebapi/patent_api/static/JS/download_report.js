function downloadReport() {
  var searchKeyword = getSearchKeyword()

  fetch(`/get_report_data/?searchKeyword=${searchKeyword}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((response) => {
      if (response.ok) {
        return response.json()
      }
      throw new Error('Network response was not ok.')
    })
    .then((reportData) => {
      return fetch('/generate_pdf/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(reportData),
      })
    })
    .then((response) => {
      if (response.ok) {
        return response.blob()
      }
      throw new Error('Network response was not ok.')
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${searchKeyword} report.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
    })
    .catch((error) => {
      console.error('Error:', error)
    })
}

function getSearchKeyword() {
  var params = new URLSearchParams(window.location.search)
  return params.get('q')
}

function getCSRFToken() {
  let cookieValue = null
  let name = 'csrftoken'
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}
