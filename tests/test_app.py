import unittest
import subprocess
from unittest.mock import patch, MagicMock, ANY
from flask import session
from app import app, url_list, run_command


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_add_url(self):
        response = self.app.post(
            '/add_url', json={'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('http://example.com', response.json['url_list'])

    def test_remove_url(self):
        url_list.append('http://example.com')
        response = self.app.post(
            '/remove_url', json={'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('http://example.com', response.json['url_list'])

    def test_start_transcode(self):
        with self.app as client:
            response = client.post(
                '/start_transcode', data={'formats': ['flac']})
            self.assertEqual(response.status_code, 200)
            self.assertIn('id', session)

    def test_url_list_display(self):
        url_list.append('http://example.com')
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('http://example.com', response.get_data(as_text=True))

    @patch('app.socketio.emit')
    def test_console_output(self, mock_emit):
        with self.app as client:
            response = client.post(
                '/start_transcode', data={'formats': ['flac']})
            self.assertEqual(response.status_code, 200)
            mock_emit.assert_any_call(
                'command_output', {'data': 'output line 1\n'}, to=ANY)
            mock_emit.assert_any_call(
                'command_output', {'data': 'output line 2\n'}, to=ANY)

    @patch('app.subprocess.Popen')
    @patch('app.DiscordWebhook')
    @patch('app.socketio.emit')
    def test_run_command(self, mock_emit, mock_discord_webhook, mock_popen):
        # Mock the Popen object and its methods
        mock_process = MagicMock()
        mock_process.stdout = iter(["output line 1\n", "output line 2\n"])
        mock_process.stderr = iter(["error line 1\n"])
        mock_popen.return_value = mock_process

        # Mock the DiscordWebhook object and its methods
        mock_webhook_instance = MagicMock()
        mock_discord_webhook.return_value = mock_webhook_instance

        # Define the command and session_id
        command = ["echo", "test"]
        session_id = "test_session_id"

        # Call the function
        run_command(command, session_id)

        # Assertions to check if subprocess.Popen was called with the correct command
        mock_popen.assert_called_once_with(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')

        # Assertions to check if DiscordWebhook was called and executed
        mock_discord_webhook.assert_called()
        mock_webhook_instance.execute.assert_called()

        # Assertions to check if socketio.emit was called with the correct parameters
        mock_emit.assert_any_call(
            'command_output', {'data': 'output line 1\n'}, to=session_id)
        mock_emit.assert_any_call(
            'command_output', {'data': 'output line 2\n'}, to=session_id)
        mock_emit.assert_any_call(
            'command_output', {'data': 'error line 1\n'}, to=session_id)


if __name__ == '__main__':
    unittest.main()
