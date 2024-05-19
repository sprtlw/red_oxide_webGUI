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
