/*$(document).ready(function () {
  function handleMp3Change() {
    if ($('#mp3320').is(':checked') || $('#mp3-v0').is(':checked')) {
      $('#flac').prop('checked', false)
    }
  }

  function handleFlacChange() {
    if ($('#flac').is(':checked')) {
      $('#mp3320, #mp3-v0').prop('checked', false)
    }
  }

  $('#mp3320, #mp3-v0').change(function () {
    handleMp3Change()
  })

  $('#flac').change(function () {
    handleFlacChange()
  })

  // Initial checks in case of pre-checked boxes
  handleMp3Change()
  handleFlacChange()
})
*/

$(document).ready(function () {
  // Initialize socket connection
  var socket = io.connect('http://' + document.domain + ':' + location.port)
  var sessionId = $('#session-id').val()

  // Emit join event when socket connects
  socket.on('connect', function () {
    socket.emit('join', { session_id: sessionId })
  })

  // Display command output received from server
  socket.on('command_output', function (msg) {
    $('#command-output').append('<p>' + msg.data + '</p>')
    $('#command-output').scrollTop($('#command-output')[0].scrollHeight) // Auto-scroll to bottom
  })

  // Submit form to clear output and emit leave event
  $('#transcode-form').submit(function () {
    $('#command-output').empty() // Clear the output container
    socket.emit('leave', { session_id: sessionId })
  })
})

$(document).ready(function () {
  // Function to add a new URL
  function addUrl() {
    const newUrl = $('#new-url').val()
    $.ajax({
      type: 'POST',
      url: '/add_url',
      data: JSON.stringify({ url: newUrl }),
      contentType: 'application/json',
      success: function (response) {
        $('#url-list').html('')
        response.url_list.forEach(function (url) {
          $('#url-list').append(
            '<div class="url-item" data-url="' +
              url +
              '"><span>' +
              url +
              '</span><button class="remove-btn" onclick="removeUrl(\'' +
              url +
              '\')">X</button></div>'
          )
        })
        $('#new-url').val('')
      },
    })
  }

  // Function to remove a URL
  function removeUrl(urlToRemove) {
    $.ajax({
      type: 'POST',
      url: '/remove_url',
      data: JSON.stringify({ url: urlToRemove }),
      contentType: 'application/json',
      success: function (response) {
        $('#url-list').html('')
        response.url_list.forEach(function (url) {
          $('#url-list').append(
            '<div class="url-item" data-url="' +
              url +
              '"><span>' +
              url +
              '</span><button class="remove-btn" onclick="removeUrl(\'' +
              url +
              '\')">X</button></div>'
          )
        })
      },
    })
  }

  // Click event for adding URL
  $('#add-url-button').click(function () {
    addUrl()
  })

  // Keypress event for adding URL on Enter key press
  $('#new-url').keypress(function (e) {
    if (e.which == 13) {
      // Enter key pressed
      addUrl()
      return false // Prevent form submission
    }
  })

  // Click event for removing URL
  $(document).on('click', '.url-item', function () {
    const urlToRemove = $(this).data('url')
    $.ajax({
      type: 'POST',
      url: '/remove_url',
      data: JSON.stringify({ url: urlToRemove }),
      contentType: 'application/json',
      success: function (response) {
        $('#url-list').html('')
        response.url_list.forEach(function (url) {
          $('#url-list').append(
            '<div class="url-item" data-url="' +
              url +
              '"><span>' +
              url +
              '</span><button class="remove-btn" onclick="removeUrl(\'' +
              url +
              '\')">X</button></div>'
          )
        })
      },
    })
  })
})

$(document).ready(function () {
  // Function to handle file upload
  function uploadUrlFile(file) {
    const reader = new FileReader()
    reader.onload = function (event) {
      const urls = event.target.result
        .split('\n')
        .filter((url) => url.trim() !== '')
      $.ajax({
        type: 'POST',
        url: '/upload_url_file',
        data: JSON.stringify({ urls: urls }),
        contentType: 'application/json',
        success: function (response) {
          $('#url-list').html('')
          response.url_list.forEach(function (url) {
            $('#url-list').append(
              '<div class="url-item" data-url="' +
                url +
                '"><span>' +
                url +
                '</span><button class="remove-btn" onclick="removeUrl(\'' +
                url +
                '\')">X</button></div>'
            )
          })
        },
      })
    }
    reader.readAsText(file)
  }

  // Click event for uploading URL file
  $('#upload-url-file-button').click(function () {
    const file = $('#url-file')[0].files[0]
    if (file) {
      uploadUrlFile(file)
    }
  })
})
