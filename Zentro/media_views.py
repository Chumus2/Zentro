import mimetypes
import re
from pathlib import Path

from django.http import FileResponse, Http404, HttpResponse
from django.utils._os import safe_join
from django.utils.http import http_date


RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)$")
CHUNK_SIZE = 8192


def _range_file(file_obj, start, length, chunk_size=CHUNK_SIZE):
    file_obj.seek(start)
    remaining = length

    while remaining > 0:
        chunk = file_obj.read(min(chunk_size, remaining))
        if not chunk:
            break
        remaining -= len(chunk)
        yield chunk


def serve_media(request, path, document_root):
    normalized_path = Path(safe_join(document_root, path))

    if normalized_path.is_dir() or not normalized_path.exists():
        raise Http404("File does not exist.")

    stat = normalized_path.stat()
    file_size = stat.st_size
    content_type, encoding = mimetypes.guess_type(str(normalized_path))
    content_type = content_type or "application/octet-stream"
    range_header = request.headers.get("Range", "").strip()

    if range_header:
        match = RANGE_RE.fullmatch(range_header)
        if not match:
            response = HttpResponse(status=416)
            response.headers["Content-Range"] = f"bytes */{file_size}"
            response.headers["Accept-Ranges"] = "bytes"
            return response

        start_str, end_str = match.groups()

        if start_str == "" and end_str == "":
            response = HttpResponse(status=416)
            response.headers["Content-Range"] = f"bytes */{file_size}"
            response.headers["Accept-Ranges"] = "bytes"
            return response

        if start_str == "":
            length = min(int(end_str), file_size)
            start = max(file_size - length, 0)
            end = file_size - 1
        else:
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

        if start >= file_size or start < 0 or end < start:
            response = HttpResponse(status=416)
            response.headers["Content-Range"] = f"bytes */{file_size}"
            response.headers["Accept-Ranges"] = "bytes"
            return response

        end = min(end, file_size - 1)
        length = end - start + 1
        file_obj = normalized_path.open("rb")
        response = FileResponse(
            _range_file(file_obj, start, length),
            status=206,
            content_type=content_type,
        )
        response.headers["Content-Length"] = str(length)
        response.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
    else:
        response = FileResponse(normalized_path.open("rb"), content_type=content_type)
        response.headers["Content-Length"] = str(file_size)

    response.headers["Accept-Ranges"] = "bytes"
    response.headers["Last-Modified"] = http_date(stat.st_mtime)

    if encoding:
        response.headers["Content-Encoding"] = encoding

    return response
