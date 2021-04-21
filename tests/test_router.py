from parameterized import parameterized
from httpx import AsyncClient
from server.server import app
import unittest
from unittest.mock import patch, AsyncMock


class TestRouter(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"challenger": "Ana", "challenged": "Pepe"}, 200),
    ])
    async def test_challenge(self, data, status):
        with patch('uuid.uuid4', return_value='810a84e7'):
            with patch('server.websockets.notify_challenge_to_client', new_callable=AsyncMock) as mock:
                async with AsyncClient(app=app, base_url="http://test") as ac:
                    response = await ac.post(
                        "/challenge",
                        json=data
                    )
                mock.assert_called_once_with('Ana', 'Pepe', '810a84e7')
        assert response.status_code == status
        assert response.json() == data
