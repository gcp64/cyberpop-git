"""
Cyberpop UI Module
Defines visual aesthetics, color palettes, panels, tables, and spinner controls
inspired by the Cyberpunk genre using the `rich` library.
"""

import sys
import re

# Reconfigure stdout and stderr to UTF-8 on Windows to avoid UnicodeEncodeError in standard terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align
import subprocess
import arabic_reshaper
from bidi.algorithm import get_display

console = Console()

def _shape_line_preserving_tags(line: str) -> str:
    """Helper to shape a single line of text while keeping Rich style tags intact."""
    tag_pattern = re.compile(r'(\[/?(?:[a-zA-Z0-9#_/ ]+)?\])')
    
    # Find all tags
    tags = tag_pattern.findall(line)
    if not tags:
        return get_display(arabic_reshaper.reshape(line))
        
    # Replace tags with unique placeholders
    text_with_placeholders = line
    placeholders = []
    for idx, tag in enumerate(tags):
        placeholder = f"XYZTAG{idx}XYZ"
        placeholders.append((placeholder, tag))
        text_with_placeholders = text_with_placeholders.replace(tag, placeholder, 1)
        
    # Reshape and apply BiDi
    reshaped = arabic_reshaper.reshape(text_with_placeholders)
    bidi_text = get_display(reshaped)
    
    # Restore the tags
    final_text = bidi_text
    for placeholder, tag in placeholders:
        final_text = final_text.replace(placeholder, tag)
        
    return final_text

def ar(text: str) -> str:
    """Shapes and reorders Arabic text for LTR terminals, preserving Rich markup tags. Bypasses LTR/English text."""
    if not text:
        return ""
    # Optimization: Bypass shaping if string contains no Arabic characters
    if not any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in text):
        return text
    try:
        # If there are newlines, process line by line to preserve layout (especially for Markdown)
        if "\n" in text:
            lines = text.split("\n")
            shaped_lines = []
            for line in lines:
                line = line.rstrip("\r")
                # Handle common markdown prefixes
                prefix = ""
                for p in ["- ", "* ", "### ", "## ", "# "]:
                    if line.startswith(p):
                        prefix = p
                        line = line[len(p):]
                        break
                shaped_line = prefix + _shape_line_preserving_tags(line)
                shaped_lines.append(shaped_line)
            return "\n".join(shaped_lines)
        
        return _shape_line_preserving_tags(text)
    except Exception:
        return text

def copy_to_clipboard(text: str) -> bool:
    """Copies text to the system clipboard in a zero-dependency way."""
    if not text:
        return False
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            # Define Windows APIs
            OpenClipboard = ctypes.windll.user32.OpenClipboard
            OpenClipboard.argtypes = [wintypes.HWND]
            OpenClipboard.restype = wintypes.BOOL

            EmptyClipboard = ctypes.windll.user32.EmptyClipboard
            EmptyClipboard.argtypes = []
            EmptyClipboard.restype = wintypes.BOOL

            CloseClipboard = ctypes.windll.user32.CloseClipboard
            CloseClipboard.argtypes = []
            CloseClipboard.restype = wintypes.BOOL

            GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
            GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
            GlobalAlloc.restype = wintypes.HGLOBAL

            GlobalLock = ctypes.windll.kernel32.GlobalLock
            GlobalLock.argtypes = [wintypes.HGLOBAL]
            GlobalLock.restype = wintypes.LPVOID

            GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
            GlobalUnlock.argtypes = [wintypes.HGLOBAL]
            GlobalUnlock.restype = wintypes.BOOL

            SetClipboardData = ctypes.windll.user32.SetClipboardData
            SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
            SetClipboardData.restype = wintypes.HANDLE

            GMEM_MOVEABLE = 0x0002
            CF_UNICODETEXT = 13

            if not OpenClipboard(None):
                return False
            try:
                EmptyClipboard()
                # Use UTF-16 LE encoding with null-terminator for Windows Unicode clipboard
                encoded = (text + '\0').encode('utf-16le')
                h_global = GlobalAlloc(GMEM_MOVEABLE, len(encoded))
                if not h_global:
                    return False
                ptr = GlobalLock(h_global)
                if ptr:
                    ctypes.memmove(ptr, encoded, len(encoded))
                    GlobalUnlock(h_global)
                    SetClipboardData(CF_UNICODETEXT, h_global)
                    return True
                return False
            finally:
                CloseClipboard()
        elif sys.platform == "darwin":
            process = subprocess.Popen('pbcopy', stdin=subprocess.PIPE)
            process.communicate(input=text.encode('utf-8'))
            return process.returncode == 0
        else:
            for cmd in ['xclip -selection clipboard', 'xclip', 'xsel -b', 'xsel']:
                try:
                    parts = cmd.split()
                    process = subprocess.Popen(parts, stdin=subprocess.PIPE)
                    process.communicate(input=text.encode('utf-8'))
                    if process.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            return False
    except Exception:
        return False

LOGO = r"""
  ______      __                                      ______ _ __ 
 / ____/_  __/ /_  ___  _________  ____  ____        / ____/(_) /_
/ /   / / / / __ \/ _ \/ ___/ __ \/ __ \/ __ \______/ / __ / / __/
/ /___/ /_/ / /_/ /  __/ /  / /_/ / /_/ / /_/ /_____/ /_/ // / /_  
\____/\__, /_.___/\___/_/  / .___/ .___/ .___/      \____//_/\__/  
     /____/               /_/   /_/   /_/                          
"""

def print_logo():
    """Prints the Cyberpunk ASCII Logo with a beautiful gradient effect."""
    logo_lines = LOGO.strip("\n").split("\n")
    styled_logo = Text()
    
    # Apply vertical gradient effect (Pink to Cyan)
    colors = ["#ff007f", "#d816a7", "#b02acf", "#883df6", "#5d50fd", "#00f0ff"]
    for i, line in enumerate(logo_lines):
        color = colors[i % len(colors)]
        styled_logo.append(line + "\n", style=f"bold {color}")
        
    border_styled = Panel(
        Align.center(styled_logo),
        border_style="bold #8a2be2",
        title=f"[bold #ffe600]▼ {ar('AI-POWERED GIT SYSTEM v1.0.0')} ▼[/bold #ffe600]",
        subtitle=f"[bold #00f0ff]{ar('Local-First • Zero-Knowledge Crypto • High-Performance Automation')}[/bold #00f0ff]",
        title_align="center",
        subtitle_align="center",
        padding=(1, 2)
    )
    console.print(border_styled)

def print_success(message: str, title: str = "SUCCESS"):
    """Prints an Acid Green success panel."""
    text = Text(ar(message), style="bold #ffffff")
    panel = Panel(
        text,
        title=f"[bold #39ff14]✔ {ar(title)}[/bold #39ff14]",
        border_style="bold #39ff14",
        padding=(0, 2),
        expand=False
    )
    console.print()
    console.print(panel)

def print_error(message: str, title: str = "SYSTEM ERROR"):
    """Prints a Neon Pink error panel with warning emojis."""
    text = Text(ar(message), style="bold #ffffff")
    panel = Panel(
        text,
        title=f"[bold #ff007f]🗲 {ar(title)}[/bold #ff007f]",
        border_style="bold #ff007f",
        padding=(0, 2),
        expand=False
    )
    console.print()
    console.print(panel)

def print_info(message: str, title: str = "SYSTEM NOTICE"):
    """Prints an Electric Cyan info panel."""
    text = Text(ar(message), style="bold #ffffff")
    panel = Panel(
        text,
        title=f"[bold #00f0ff]ℹ {ar(title)}[/bold #00f0ff]",
        border_style="bold #00f0ff",
        padding=(0, 2),
        expand=False
    )
    console.print()
    console.print(panel)

def print_warning(message: str, title: str = "WARNING"):
    """Prints a Cyber Yellow warning panel."""
    text = Text(ar(message), style="bold #ffffff")
    panel = Panel(
        text,
        title=f"[bold #ffe600]⚠ {ar(title)}[/bold #ffe600]",
        border_style="bold #ffe600",
        padding=(0, 2),
        expand=False
    )
    console.print()
    console.print(panel)

def print_commit_panel(commit_msg: str, diff_summary: str = ""):
    """Displays generated commit message inside a gorgeous glassmorphism-styled panel."""
    content = Text()
    content.append("\n" + ar("💡 Proposed Conventional Commit Message:") + "\n", style="bold #00f0ff")
    content.append(f"  {commit_msg}\n\n", style="bold #ffe600")
    
    if diff_summary:
        content.append(ar("📊 Commit Insights & Changes Summary:") + "\n", style="bold #ff007f")
        content.append(f"  {ar(diff_summary)}\n", style="italic #ffffff")
        
    panel = Panel(
        content,
        title=f"[bold #8a2be2]⚡ {ar('AI Cognitive Output')} ⚡[/bold #8a2be2]",
        border_style="bold #8a2be2",
        padding=(0, 2),
        expand=True
    )
    console.print()
    console.print(panel)

def render_table(title: str, headers: list[str], rows: list[list[str]], no_wrap_all: bool = False):
    """Renders a beautiful cyberpunk data table."""
    table = Table(
        title=f"[bold #ffe600]▲ {ar(title)} ▲[/bold #ffe600]",
        title_style="bold #ffe600",
        border_style="bold #8a2be2",
        header_style="bold #00f0ff",
        show_lines=True
    )
    
    for header in headers:
        header_ar = ar(header)
        # Determine if we should prevent wrapping on this column (commands, examples, hashes, variables)
        is_no_wrap = no_wrap_all or any(w in header.lower() or w in header_ar for w in ["command", "hash", "مثال", "أمر", "الالتزام", "المتغير", "variable", "key", "مفتاح"])
        table.add_column(header_ar, justify="left", no_wrap=is_no_wrap)
        
    for row in rows:
        table.add_row(*[ar(cell) for cell in row])
        
    console.print()
    console.print(table)

class CyberSpinner:
    """A context-manager like wrapper for displaying a stylish neon progress spinner."""
    def __init__(self, message: str, color: str = "#ff007f"):
        self.message = message
        self.color = color
        self.live = None

    def __enter__(self):
        spinner = Spinner("dots", text=Text(ar(self.message), style=f"bold {self.color}"))
        self.live = Live(spinner, refresh_per_second=15, transient=True)
        self.live.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.live:
            self.live.stop()
