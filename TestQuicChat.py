import unittest
from unittest.mock import MagicMock, patch
import socket
import QuicFunc
from QuicPackage import QuicPackage

class TestQuicChat(unittest.TestCase):

    def setUp(self):
        self.client_address = ('localhost', 12345)  # Address to send messages to

    # Existing tests remain unchanged...

    def test_incorrect_package_format(self):
        """Test the handling of incorrectly formatted package data."""
        bad_data = b"BAD_FORMAT&MissingParts"
        with patch('socket.socket') as MockSocket:
            mock_socket = MockSocket.return_value
            mock_socket.recvfrom.return_value = (bad_data, self.client_address)
            self.assertRaises(ValueError, QuicFunc.recreate_package, bad_data)

    def test_connection_timeout(self):
        """Ensure that a timeout exception is raised appropriately."""
        with patch('socket.socket') as MockSocket:
            mock_socket = MockSocket.return_value
            mock_socket.recvfrom.side_effect = socket.timeout
            self.assertRaises(socket.timeout, mock_socket.recvfrom)


    def test_full_message_cycle(self):
        """Test a complete send-receive-acknowledge cycle."""
        with patch('socket.socket') as MockSocket:
            mock_socket = MockSocket.return_value
            # Sending a package
            send_package = QuicPackage(0, "Complete Cycle Test",1)
            QuicFunc.send_package(send_package, mock_socket, self.client_address)

            # Simulating a receive
            mock_socket.recvfrom.return_value = (b"TEXT&0&0.0&Complete Cycle Test&1", self.client_address)
            receive_package = QuicFunc.recreate_package(mock_socket.recvfrom()[0])
            self.assertEqual(receive_package.payload, "Complete Cycle Test")

            # Simulating sending an ACK
            QuicFunc.send_package(QuicPackage(0, "ACK",1), mock_socket, self.client_address)
            self.assertTrue(mock_socket.sendto.called)

    def test_edge_case_package_handling(self):
        """Test sending and receiving edge case data, like empty or very large payloads."""
        with patch('socket.socket') as MockSocket:
            mock_socket = MockSocket.return_value
            # Testing with an empty payload
            empty_package = QuicPackage(0, "",1)
            QuicFunc.send_package(empty_package, mock_socket, self.client_address)
            self.assertTrue(mock_socket.sendto.called)

            # Testing with a large payload
            large_package = QuicPackage(0, "a" * 65535,1)  # Max UDP packet size edge case
            QuicFunc.send_package(large_package, mock_socket, self.client_address)
            self.assertTrue(mock_socket.sendto.called)

    def test_high_volume_package_handling(self):
        """Test handling of high volume of packages."""
        with patch('socket.socket') as MockSocket:
            mock_socket = MockSocket.return_value
            # Simulate receiving multiple packets rapidly
            mock_socket.recvfrom.side_effect = [(b"TEXT&1&0.0&Hello&1", self.client_address)] * 100
            for _ in range(100):
                package = QuicFunc.recreate_package(mock_socket.recvfrom()[0])
                self.assertEqual(package.payload, "Hello")


if __name__ == "_main_":
    unittest.main()