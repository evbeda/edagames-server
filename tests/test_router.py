from parameterized import parameterized
from httpx import AsyncClient
from server.server import app
import unittest


class TestRouter(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"challenger": "Ana", "challenged": "Pepe"}, 200),
    ])
    async def test_challenge(self, data, status):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/challenge",
                json=data
            )
        assert response.status_code == status
        assert response.json() == ['Challenge received OK']
