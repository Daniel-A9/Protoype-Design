"""
Views for serving static HTML files from docs folder
"""
from django.http import FileResponse, Http404
from django.conf import settings
from pathlib import Path
import os


def serve_docs(request, path=''):
    """
    Serve static HTML files from the docs folder
    """
    # Get the docs directory
    docs_dir = settings.BASE_DIR.parent / 'docs'
    
    # Normalize the path
    if not path:
        path = 'index.html'
    elif path.endswith('/'):
        path = path + 'index.html'
    elif not path.endswith('.html') and '.' not in os.path.basename(path):
        # If it's a directory path without trailing slash, add index.html
        path = path + '/index.html'
    
    # Build the file path
    file_path = docs_dir / path
    
    # Security: Make sure the resolved path is within docs_dir
    try:
        file_path = file_path.resolve()
        docs_dir = docs_dir.resolve()
        if not str(file_path).startswith(str(docs_dir)):
            raise Http404("Page not found")
    except (OSError, ValueError):
        raise Http404("Page not found")
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        raise Http404("Page not found")
    
    # Determine content type
    content_type = 'text/html'
    if file_path.suffix == '.css':
        content_type = 'text/css'
    elif file_path.suffix == '.js':
        content_type = 'application/javascript'
    elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        content_type = f'image/{file_path.suffix[1:]}'
    
    # Serve the file
    return FileResponse(open(file_path, 'rb'), content_type=content_type)

