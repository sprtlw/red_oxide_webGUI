$(document).ready(function () {
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

$(document).ready(function () {
  var socket = io.connect('http://' + document.domain + ':' + location.port)
  var sessionId = $('#session-id').val()

  socket.on('connect', function () {
    socket.emit('join', { session_id: sessionId })
  })

  socket.on('command_output', function (msg) {
    $('#command-output').append('<p>' + msg.data + '</p>')
  })

  $('#transcode-form').submit(function () {
    $('#command-output').empty() // Clear the output container
    socket.emit('leave', { session_id: sessionId })
  })
})
