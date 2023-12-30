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

// function saveUserNotes() {}

function getChartData() {
  return {
    distributionLineChart: localStorage.getItem('distributionLineChart'),
    distributionBarChart: localStorage.getItem('distributionBarChart'),
    titleText1: localStorage.getItem('titleText1'),
    titleText2: localStorage.getItem('titleText2'),
    distributionText: localStorage.getItem('distributionText'),
    innovationBarChart: localStorage.getItem('innovationBarChart'),
    innovationMapChart: localStorage.getItem('innovationMapChart'),
    titleText3: localStorage.getItem('titleText3'),
    titleText4: localStorage.getItem('titleText4'),
    innovationText: localStorage.getItem('innovationText'),
    networkChart: localStorage.getItem('networkChart'),
    titleText5: localStorage.getItem('titleText5'),
    networkText: localStorage.getItem('networkText'),
    titleText6: localStorage.getItem('titleText6'),
    wordcloudImage: localStorage.getItem('wordcloud'),
  }
}

// function fetchGPTConclusion(searchKeyword, base64Images) {
//   fetch('/gpt_request/', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({
//       text: `以下是关于搜索词“${searchKeyword}”在专利集合中的搜索结果，以下图片可能涉及这个专利的1.年度分布，2.领域创新主体计量/分布，3.领域合作网络及测度中任何一种图。作为一名数据分析师，请根据获得的图的类型描述图中的具体信息并进行分析， 比如峰谷值。字数控制在50字左右。`,
//       base64_images: base64Images,
//     }),
//   })
//     .then((response) => {
//       if (!response.ok) {
//         throw new Error('Network response was not ok')
//       }
//       return response.json()
//     })
//     .then((data) => {
//       // 在这里处理 GPT-4 返回的结论
//       document.getElementById('write-area').innerText = data.response
//       console.log(data.response) // 显示 GPT-4 返回的文本
//     })
//     .catch((error) => {
//       console.error('Error:', error)
//       document.getElementById('write-area').innerText =
//         'Error generating conclusion.'
//     })
// }

function saveChartData(chartId, chartInstance) {
  chartInstance.on('finished', function () {
    var imageData = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff',
    })

    localStorage.setItem(chartId, imageData)
  })
}

function downloadReport() {
  var chartData = getChartData()

  var reportData = {
    charts: [
      {
        title: chartData.titleText1,
        imageData: chartData.distributionlineChartData,
      },
      {
        title: chartData.titleText2,
        imageData: chartData.distributionbarChartData,
      },
      {
        title: chartData.titleText3,
        imageData: chartData.innovationBarChartData,
      },
      {
        title: chartData.titleText4,
        imageData: chartData.innovationMapChartData,
      },
      { title: chartData.titleText5, imageData: chartData.networkChartData },
    ],
    text:
      chartData.distributionText +
      '\n' +
      chartData.innovationText +
      '\n' +
      chartData.networkText,
  }

  fetch('/generate_pdf/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
    body: JSON.stringify(reportData),
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
      a.download = 'report.pdf'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      a.remove()
    })
    .catch((error) => {
      console.error('Error:', error)
    })
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
