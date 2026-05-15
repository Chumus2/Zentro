from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import RequestFactory, TestCase

from Zentro.media_views import serve_media


class ServeMediaTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.temp_dir = TemporaryDirectory()
        self.media_root = Path(self.temp_dir.name)
        self.media_file = self.media_root / "sample.mp4"
        self.media_file.write_bytes(b"0123456789")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_returns_full_file_without_range(self):
        request = self.factory.get("/media/sample.mp4")

        response = serve_media(request, "sample.mp4", self.media_root)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Accept-Ranges"], "bytes")
        self.assertEqual(response.headers["Content-Length"], "10")
        self.assertEqual(b"".join(response.streaming_content), b"0123456789")

    def test_returns_partial_content_for_range_requests(self):
        request = self.factory.get(
            "/media/sample.mp4",
            HTTP_RANGE="bytes=2-5",
        )

        response = serve_media(request, "sample.mp4", self.media_root)

        self.assertEqual(response.status_code, 206)
        self.assertEqual(response.headers["Accept-Ranges"], "bytes")
        self.assertEqual(response.headers["Content-Range"], "bytes 2-5/10")
        self.assertEqual(response.headers["Content-Length"], "4")
        self.assertEqual(b"".join(response.streaming_content), b"2345")

