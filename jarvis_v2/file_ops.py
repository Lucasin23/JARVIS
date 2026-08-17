"""
File Operations Module — Create, read, list, and search files.
Gives JARVIS the ability to manage files on your computer.
"""

import os
import glob
import shutil
from datetime import datetime


# Safety: restrict file operations to the user's home directory by default
HOME = os.path.expanduser("~")

# Directories that require explicit confirmation (system-critical)
PROTECTED_DIRS = [
    "/System", "/usr", "/bin", "/sbin", "/etc",
    "/private/var", "/Library/System",
]


def _is_safe_path(path: str) -> bool:
    """Check if a path is within the user's home directory."""
    expanded = os.path.expanduser(path)
    abs_path = os.path.abspath(expanded)
    return abs_path.startswith(HOME)


def _extract_path(text: str, prefixes: list[str]) -> str | None:
    """Extract a file path from user input after one of the given prefixes."""
    text_lower = text.lower()
    for prefix in prefixes:
        if prefix in text_lower:
            idx = text_lower.index(prefix) + len(prefix)
            path = text[idx:].strip()
            # Strip common trailing words
            for word in [" please", " for me", " now"]:
                if path.lower().endswith(word):
                    path = path[: -len(word)].strip()
            if path:
                return path
    return None


# ---------------------------------------------------------------------------
# File Creation
# ---------------------------------------------------------------------------

def create_file(text: str) -> str:
    """Create a new file (optionally with content)."""
    # Extract filename — supports "create file notes.txt" or "create file notes.txt with content hello world"
    path = _extract_path(text, [
        "create file", "make file", "new file", "create a file", "make a file"
    ])
    if not path:
        return "What file would you like me to create? Example: create file notes.txt"

    # Check for "with content" or "containing"
    content = ""
    for sep in [" with content ", " containing ", " content "]:
        if sep in path.lower():
            idx = path.lower().index(sep)
            content = path[idx + len(sep):]
            path = path[:idx].strip()
            break

    filepath = os.path.expanduser(path)
    if not _is_safe_path(filepath):
        return f"For safety, I can only create files in your home directory, sir."

    if os.path.exists(filepath):
        return f"File '{path}' already exists, sir."

    try:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content)
        return f"Created file '{path}', sir."
    except Exception as e:
        return f"I couldn't create '{path}': {e}"


def create_folder(text: str) -> str:
    """Create a new folder/directory."""
    path = _extract_path(text, [
        "create folder", "make folder", "new folder", "create directory",
        "make directory", "create a folder", "make a folder"
    ])
    if not path:
        return "What folder would you like me to create? Example: create folder Projects"

    folderpath = os.path.expanduser(path)
    if not _is_safe_path(folderpath):
        return "For safety, I can only create folders in your home directory, sir."

    if os.path.exists(folderpath):
        return f"Folder '{path}' already exists, sir."

    try:
        os.makedirs(folderpath, exist_ok=True)
        return f"Created folder '{path}', sir."
    except Exception as e:
        return f"I couldn't create folder '{path}': {e}"


# ---------------------------------------------------------------------------
# File Reading
# ---------------------------------------------------------------------------

def read_file(text: str) -> str:
    """Read and display the contents of a file."""
    path = _extract_path(text, [
        "read file", "show file", "cat file", "open file", "display file",
        "read the file", "show me the file"
    ])
    if not path:
        return "Which file would you like me to read? Example: read file notes.txt"

    filepath = os.path.expanduser(path)
    if not os.path.exists(filepath):
        return f"I couldn't find '{path}', sir."

    try:
        with open(filepath, "r") as f:
            content = f.read()
        if len(content) > 2000:
            content = content[:2000] + "\n... (truncated, file is longer)"
        return f"Contents of '{path}':\n\n{content}"
    except Exception as e:
        return f"I couldn't read '{path}': {e}"


# ---------------------------------------------------------------------------
# File Listing
# ---------------------------------------------------------------------------

def list_files(text: str) -> str:
    """List files in a directory."""
    path = _extract_path(text, [
        "list files", "show files", "list directory", "show directory",
        "what's in", "list folder", "show folder", "ls "
    ])

    if not path:
        # Default to home directory
        folderpath = HOME
        display_path = "~"
    else:
        folderpath = os.path.expanduser(path)
        display_path = path
        if not os.path.exists(folderpath):
            return f"I couldn't find directory '{path}', sir."

    try:
        items = sorted(os.listdir(folderpath))
        if not items:
            return f"The directory '{display_path}' is empty, sir."

        # Separate files and folders
        folders = []
        files = []
        for item in items:
            full_path = os.path.join(folderpath, item)
            if os.path.isdir(full_path):
                folders.append(f"  [FOLDER]  {item}")
            else:
                files.append(f"  [FILE]    {item}")

        result = f"Contents of '{display_path}':\n"
        result += "\n".join(folders)
        if folders and files:
            result += "\n"
        result += "\n".join(files)
        return result
    except Exception as e:
        return f"I couldn't list '{display_path}': {e}"


# ---------------------------------------------------------------------------
# File Search
# ---------------------------------------------------------------------------

def search_files(text: str) -> str:
    """Search for files by name pattern in the home directory."""
    pattern = _extract_path(text, [
        "search for files", "find files", "search files",
        "find file", "search for file"
    ])
    if not pattern:
        return "What file pattern would you like me to search for? Example: find files *.txt"

    try:
        # Search in home directory recursively
        search_pattern = os.path.join(HOME, "**", pattern)
        matches = glob.glob(search_pattern, recursive=True)

        if not matches:
            # Try as filename contains
            all_files = glob.glob(os.path.join(HOME, "**", "*"), recursive=True)
            matches = [f for f in all_files if pattern.lower() in os.path.basename(f).lower()][:20]

        if not matches:
            return f"No files matching '{pattern}' found, sir."

        # Limit results
        matches = matches[:30]
        result = f"Found {len(matches)} file(s) matching '{pattern}':\n"
        for m in matches:
            rel = os.path.relpath(m, HOME)
            result += f"  ~/{rel}\n"
        return result.strip()
    except Exception as e:
        return f"Error searching files: {e}"


# ---------------------------------------------------------------------------
# File Deletion
# ---------------------------------------------------------------------------

def delete_file(text: str) -> str:
    """Delete a file (moves to trash on macOS, deletes on others)."""
    path = _extract_path(text, [
        "delete file", "remove file", "delete the file", "remove the file"
    ])
    if not path:
        return "Which file would you like me to delete? Example: delete file old_notes.txt"

    filepath = os.path.expanduser(path)
    if not _is_safe_path(filepath):
        return "For safety, I can only delete files in your home directory, sir."

    if not os.path.exists(filepath):
        return f"I couldn't find '{path}', sir."

    try:
        # On macOS, move to trash using send2trash if available, otherwise delete
        try:
            import send2trash
            send2trash.send2trash(filepath)
            return f"Moved '{path}' to trash, sir."
        except ImportError:
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
            return f"Deleted '{path}', sir."
    except Exception as e:
        return f"I couldn't delete '{path}': {e}"


# ---------------------------------------------------------------------------
# File Info
# ---------------------------------------------------------------------------

def file_info(text: str) -> str:
    """Get information about a file."""
    path = _extract_path(text, [
        "file info", "info about", "details about file",
        "info about file", "file details"
    ])
    if not path:
        return "Which file would you like info about? Example: file info notes.txt"

    filepath = os.path.expanduser(path)
    if not os.path.exists(filepath):
        return f"I couldn't find '{path}', sir."

    try:
        stat = os.stat(filepath)
        size = stat.st_size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_type = "directory" if os.path.isdir(filepath) else "file"

        return (
            f"File: {path}\n"
            f"  Type: {file_type}\n"
            f"  Size: {size_str}\n"
            f"  Modified: {mod_time}\n"
            f"  Full path: {filepath}"
        )
    except Exception as e:
        return f"Error getting file info: {e}"
