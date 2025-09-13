import sys
import time
import subprocess
import os
import tomllib
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import typer
import pyfiglet
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box
from datetime import datetime
import shutil
from pathlib import Path
import http.server
import socketserver
import ssl
import threading
from jinja2 import Template

# Version of the CLI
__version__ = "0.1.0"

# Create console for beautiful output
console = Console()

class Debugger:
    """Debugger class with configurable settings"""
    
    def __init__(self, quiet: bool = False, no_color: bool = False, no_figlet: bool = False):
        self.quiet = os.environ.get('QUILLION_QUIET', '0') == '1'
        self.no_color = os.environ.get('QUILLION_NO_COLOR', '0') == '1'
        self.no_figlet = os.environ.get('QUILLION_NO_FIGLET', '0') == '1'

    def is_quiet(self) -> bool:
        """Check if debugger is in quiet mode"""
        return self.quiet

    def configure(self, quiet: Optional[bool] = None, no_color: Optional[bool] = None, no_figlet: Optional[bool] = None):
        """Update debugger configuration"""
        if quiet is not None:
            self.quiet = quiet
        if no_color is not None:
            self.no_color = no_color
        if no_figlet is not None:
            self.no_figlet = no_figlet
    
    def log_info(self, message: str):
        """Styled info log"""
        if self.quiet:
            return
        if self.no_color:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"{timestamp} │ {message.replace('[dim]', '').replace('[/]', '').replace('[cyan]', '').replace('[bold blue]', '')}")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"[bold blue]{timestamp}[/] [dim]│[/] {message}")

    def log_success(self, message: str):
        """Styled success log"""
        if self.quiet:
            return
        if self.no_color:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"{timestamp} │ ✓ {message.replace('[dim]', '').replace('[/]', '').replace('[cyan]', '')}")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"[bold blue]{timestamp}[/] [dim]│[/] [green]✓[/] {message}")

    def log_warning(self, message: str):
        """Styled warning log"""
        if self.quiet:
            return
        if self.no_color:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"{timestamp} │ ⚠  {message.replace('[dim]', '').replace('[/]', '').replace('[cyan]', '')}")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"[bold blue]{timestamp}[/] [dim]│[/] [yellow]⚠[/]  {message}")

    def log_error(self, message: str):
        """Styled error log"""
        if self.quiet:
            return
        if self.no_color:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"{timestamp} │ ✗ {message.replace('[dim]', '').replace('[/]', '').replace('[cyan]', '')}")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"[bold blue]{timestamp}[/] [dim]│[/] [red]✗[/] {message}")

    def log_version(self):
        """Display version information"""
        if self.quiet:
            return
        if self.no_color:
            console.print(f"Quillion CLI v{__version__}")
        else:
            console.print(f"[bold green]Quillion CLI[/] v[cyan]{__version__}[/]")

    def log_server_start(self, host: str, port: int, https: bool = False):
        """Beautiful server info output"""
        if self.quiet:
            return
        
        protocol = "https" if https else "http"
        ws_protocol = "wss" if https else "ws"
        
        if self.no_color:
            console.print("\n" + "─" * 80)
            console.print("Quillion Dev Server")
            console.print("─" * 80)
            console.print("🚀 Server running!")
            console.print("")
            console.print(f"Server:    {ws_protocol}://{host}:{port}")
            console.print(f"Frontend:  {protocol}://{host}:{port}")
            console.print("")
            console.print("Press Ctrl+C to stop")
            console.print("─" * 80)
        else:
            console.print("\n" + "─" * 80)
            
            server_panel = Panel(
                f"[bold green]🚀 Server running![/]\n\n"
                f"[bold]Server:[/]    [cyan]{ws_protocol}://{host}:{port}[/]\n"
                f"[bold]Frontend:[/]  [cyan]{protocol}://{host}:{port}[/]",
                box=box.ROUNDED,
                style="blue",
                title="Quillion Dev Server",
                width=78
            )
            
            console.print(server_panel, justify="center")
            console.print("[dim]Press Ctrl+C to stop[/]\n")
            console.print("─" * 80)

    def log_http_server_start(self, host: str, port: int, https: bool = False):
        """HTTP server info output"""
        if self.quiet:
            return
        
        protocol = "HTTPS" if https else "HTTP"
        
        if self.no_color:
            console.print(f"{protocol} server started on {host}:{port}")
            console.print(f"Serving static files from packages directory")
        else:
            console.print(f"[green]✓[/] [bold]{protocol} server[/] started on [cyan]{host}:{port}[/]")
            console.print(f"[dim]Serving static files from packages directory[/]")

    def display_banner(self):
        """Display beautiful banner"""
        if self.quiet or self.no_figlet:
            return
            
        result = pyfiglet.figlet_format("Q", font="slant")
            
        if self.no_color:
            console.print("\n", justify="center")
            console.print(result, justify="center")
            console.print("Quillion Command Line Interface", justify="center")
            console.print("\n", justify="center")
        else:
            text = Text(result, style="bold magenta3")
            console.print("\n", justify="center")
            console.print(text, justify="center")
            console.print(Text(" Quillion Command Line Interface ", style="bold cyan"), justify="center")
            console.print("\n", justify="center")
                

# Create global debugger instance with default settings
debugger = Debugger()
def get_debugger() -> Debugger:
    """Get the global debugger instance"""
    return debugger

app = typer.Typer(help="Quillion CLI", pretty_exceptions_enable=False)

def version_callback(value: bool):
    """Callback for version flag"""
    if value:
        debugger.log_version()
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        "-v", 
        callback=version_callback, 
        help="Show version and exit"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", 
                              help="Quiet mode - no debug output"),
    no_color: bool = typer.Option(False, "--no-color", 
                                 help="Disable colored output"),
    no_figlet: bool = typer.Option(False, "--no-figlet", 
                                  help="Disable figlet banner")
):
    """
    Quillion CLI - Development server and project management
    """
    # Update global debugger with command line options
    debugger.configure(quiet=quiet, no_color=no_color, no_figlet=no_figlet)

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback, config, debugger_instance: Debugger):
        self.restart_callback = restart_callback
        self.config = config
        self.debugger = debugger_instance
        self.ignore_patterns = config['development'].get('ignore_patterns', [])
        self.watch_extensions = config['development'].get('file_extensions', ['.py'])
        self.delay = config['development'].get('delay', 1.0)
        self.last_trigger = 0

    def should_ignore(self, path):
        for pattern in self.ignore_patterns:
            if pattern in path.replace('\\', '/'):
                return True
        return False

    def should_watch(self, path):
        if self.should_ignore(path):
            return False
        
        _, ext = os.path.splitext(path)
        return ext in self.watch_extensions

    def on_modified(self, event):
        if not event.is_directory and self.should_watch(event.src_path):
            current_time = time.time()
            if current_time - self.last_trigger > self.delay:
                self.last_trigger = current_time
                filename = os.path.basename(event.src_path)
                self.debugger.log_info(f"[dim]File changed:[/] [cyan]{filename}[/]")
                time.sleep(0.1)
                self.restart_callback()

class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that doesn't log anything"""
    
    def __init__(self, *args, **kwargs):
        self.packages_dir = kwargs.pop('packages_dir', 'packages')
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Override to disable all logging"""
        pass
    
    def log_error(self, format, *args):
        """Override to disable error logging"""
        pass
    
    def log_request(self, code='-', size='-'):
        """Override to disable request logging"""
        pass
    
    def translate_path(self, path):
        # Redirect requests to packages directory
        path = super().translate_path(path)
        relpath = os.path.relpath(path, os.getcwd())
        
        if relpath.startswith('packages/') or relpath == 'packages':
            return path
        
        # If root is requested, serve index.html from packages
        if relpath == '' or relpath == '.' or relpath.startswith('index'):
            packages_index = os.path.join(os.getcwd(), self.packages_dir, 'index.html')
            if os.path.exists(packages_index):
                return packages_index
        
        # For all other paths, try to find the file in packages
        packages_path = os.path.join(os.getcwd(), self.packages_dir, relpath)
        if os.path.exists(packages_path):
            return packages_path
        
        return path

def load_config(project_dir: str = "./", debugger_instance: Debugger = debugger):
    config_path = os.path.join(project_dir, "quillion.toml")
    
    default_config = {
        'name': 'quillion-app',
        'version': '0.1.0',
        'description': 'A Quillion web application',
        'server': {
            'entry_point': 'app.py',
            'host': '127.0.0.1',
            'port': 1337,
            'debug': True,
            'reload': True
        },
        'http_server': {
            'enabled': True,
            'host': '127.0.0.1',
            'port': 8000,
            'ssl': False,
            'ssl_cert': None,
            'ssl_key': None,
            'silent': True
        },
        'development': {
            'watch_dirs': ['.'],
            'ignore_patterns': ['__pycache__', '*.log', '*.tmp', '.git', 'node_modules'],
            'file_extensions': ['.py', '.toml', '.html', '.css', '.js', '.json'],
            'delay': 1.0
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'rb') as f:
                user_config = tomllib.load(f)
            
            merged_config = default_config.copy()
            for section, values in user_config.items():
                if section in merged_config and isinstance(merged_config[section], dict):
                    merged_config[section].update(values)
                else:
                    merged_config[section] = values
            
            debugger_instance.log_success("Configuration loaded from quillion.toml")
            return merged_config
        except Exception as e:
            debugger_instance.log_error(f"Error loading config: {e}")
            raise typer.Exit(1)
    else:
        debugger_instance.log_error("No quillion.toml found")
        raise typer.Exit(1)

def run_server(config, project_dir: str = "./", debugger_instance: Debugger = debugger):
    server_config = config['server']
    entry_point = os.path.join(project_dir, server_config['entry_point'])
    host = server_config['host']
    port = server_config['port']
    debug = server_config.get('debug', False)
    
    if not os.path.exists(entry_point):
        debugger_instance.log_error(f"Entry point not found: {entry_point}")
        return None
    
    env = os.environ.copy()
    env['QUILLION_HOST'] = host
    env['QUILLION_PORT'] = str(port)
    env['QUILLION_QUIET'] = '1' if debugger_instance.is_quiet() else '0'
    env['QUILLION_NO_COLOR'] = '1' if debugger_instance.no_color else '0'
    env['QUILLION_NO_FIGLET'] = '1' if debugger_instance.no_figlet else '0'
    
    cmd = [sys.executable, entry_point]
    
    return subprocess.Popen(cmd, cwd=project_dir, env=env)

def start_http_server(config, project_dir: str = "./", debugger_instance: Debugger = debugger):
    """Start HTTP/HTTPS server for static files"""
    http_config = config.get('http_server', {})
    
    if not http_config.get('enabled', True):
        debugger_instance.log_info("HTTP server is disabled in config")
        return None, None
    
    host = http_config.get('host', '127.0.0.1')
    port = http_config.get('port', 8000)
    use_ssl = http_config.get('ssl', False)
    ssl_cert = http_config.get('ssl_cert')
    ssl_key = http_config.get('ssl_key')
    silent = http_config.get('silent', True)
    
    # Create packages directory if it doesn't exist
    packages_dir = os.path.join(project_dir, '.q')
    
    # Change to project directory to serve files from there
    original_cwd = os.getcwd()
    os.chdir(project_dir)
    
    try:
        handler = lambda *args, **kwargs: SilentHTTPRequestHandler(*args, packages_dir='.q', **kwargs)
        httpd = socketserver.TCPServer((host, port), handler)
        
        if use_ssl:
            if ssl_cert and ssl_key:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(ssl_cert, ssl_key)
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                debugger_instance.log_success("SSL enabled for HTTP server")
            else:
                debugger_instance.log_warning("SSL enabled but no certificate provided")
        
        def run_server():
            if not silent:
                debugger_instance.log_http_server_start(host, port, use_ssl)
            httpd.serve_forever()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        return httpd, server_thread
        
    except Exception as e:
        debugger_instance.log_error(f"Failed to start HTTP server: {e}")
        os.chdir(original_cwd)
        return None, None
    finally:
        os.chdir(original_cwd)

def start_development_server(config, project_dir: str = "./", hot_reload: bool = True, debugger_instance: Debugger = debugger):
    process = run_server(config, project_dir, debugger_instance)
    if process is None:
        return

    # Start HTTP server for static files
    httpd, http_thread = start_http_server(config, project_dir, debugger_instance)

    # Output server info
    host = config['server']['host']
    port = config['server']['port']
    debugger_instance.log_server_start(host, port)

    if not hot_reload:
        process.wait()
        return

    def restart():
        nonlocal process
        if process:
            process.terminate()
            process.kill()
            process.wait()
        process = run_server(config, project_dir, debugger_instance)

    observers = []
    development_config = config['development']
    
    for watch_dir in development_config['watch_dirs']:
        full_watch_path = os.path.join(project_dir, watch_dir)
        if os.path.exists(full_watch_path):
            event_handler = ChangeHandler(restart, config, debugger_instance)
            observer = Observer()
            observer.schedule(event_handler, full_watch_path, recursive=True)
            observer.start()
            observers.append(observer)
            debugger_instance.log_info(f"[dim]Watching directory:[/] [cyan]{full_watch_path}[/]")
        else:
            debugger_instance.log_warning(f"Watch directory not found: {full_watch_path}")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        debugger_instance.log_info("Shutting down servers...")
        if process:
            process.terminate()
        if httpd:
            httpd.shutdown()
        for observer in observers:
            observer.stop()
            observer.join()

def process_templates_and_copy_files(project_dir: str, context: dict, templates_dir: Path, debugger_instance: Debugger = debugger):
    """
    Recursively process all templates in templates_dir and copy non-template files to project_dir.
    Maintains directory structure and applies context variables to .j2 files.
    Files in .templates/ go to project root, files in .templates/.q/ go to <project_dir>/.q/.
    """
    debugger_instance.log_info(f"[dim]Processing templates from:[/] [cyan]{templates_dir.resolve()}[/]")
    
    # Ensure .q/ directory exists in the project
    q_dir = Path(project_dir) / ".q"
    q_dir.mkdir(exist_ok=True)
    debugger_instance.log_success(f"Created .q directory: [cyan]{q_dir}[/]")
    
    # Check if templates_dir exists
    if not templates_dir.exists():
        debugger_instance.log_error(f"Templates directory does not exist: {templates_dir}")
        raise typer.Exit(1)
    
    # Process all files in templates directory
    for item in templates_dir.rglob("*"):
        if item.is_dir():
            continue
            
        relative_path = item.relative_to(templates_dir)
        
        # Skip hidden directories and files (except .q)
        if any(part.startswith('.') and part != '.q' for part in relative_path.parts):
            continue
            
        # Determine target path
        if relative_path.parts[0] == ".q":
            target_path = Path(project_dir) / ".q" / relative_path.relative_to(".q")
        else:
            target_path = Path(project_dir) / relative_path

        if item.is_file():
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handle template files
            if item.suffix == ".j2":
                try:
                    debugger_instance.log_info(f"[dim]Rendering template:[/] [cyan]{item}[/]")
                    template_content = item.read_text(encoding='utf-8')
                    template = Template(template_content)
                    rendered_content = template.render(**context)
                    
                    # Save without .j2 extension
                    target_file = target_path.with_suffix("")
                    target_file.write_text(rendered_content, encoding='utf-8')
                    debugger_instance.log_success(f"Rendered template: [cyan]{target_file}[/]")
                except Exception as e:
                    debugger_instance.log_error(f"Error rendering template {item}: {e}")
                    raise
            else:
                # Copy binary files and other non-template files
                try:
                    debugger_instance.log_info(f"[dim]Copying file:[/] [cyan]{item}[/]")
                    shutil.copy2(item, target_path)
                    debugger_instance.log_success(f"Copied file: [cyan]{target_path}[/]")
                except Exception as e:
                    debugger_instance.log_error(f"Error copying file {item}: {e}")
                    raise

    # Specifically handle pkg directory contents (binary files)
    pkg_templates_dir = templates_dir / ".q" / "pkg"
    pkg_target_dir = Path(project_dir) / ".q" / "pkg"
    
    if pkg_templates_dir.exists():
        pkg_target_dir.mkdir(exist_ok=True)
        debugger_instance.log_info(f"[dim]Copying pkg contents from:[/] [cyan]{pkg_templates_dir}[/]")
        
        for item in pkg_templates_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(pkg_templates_dir)
                target_path = pkg_target_dir / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(item, target_path)
                    debugger_instance.log_success(f"Copied pkg file: [cyan]{target_path}[/]")
                except Exception as e:
                    debugger_instance.log_error(f"Error copying pkg file {item}: {e}")
                    raise
                
@app.command()
def run(
    name: Optional[str] = typer.Argument(None, help="Project name or directory to run"),
    hot_reload: bool = typer.Option(True, "--hot-reload/--no-hot-reload", 
                                   help="Enable/disable hot reload functionality"),
    port: Optional[int] = typer.Option(None, "--port", "-p", 
                                      help="Override server port from config"),
    host: Optional[str] = typer.Option(None, "--host", 
                                      help="Override server host from config"),
    http_port: Optional[int] = typer.Option(None, "--http-port", 
                                           help="Override HTTP server port from config"),
    no_http: bool = typer.Option(False, "--no-http", 
                                help="Disable HTTP server for static files"),
    verbose_http: bool = typer.Option(False, "--verbose-http", 
                                     help="Enable HTTP server logging")
):
    """
    Run Quillion development server with hot reload
    """
    # Display banner with current debugger settings
    debugger.display_banner()
    
    # Determine project directory
    if name is None:
        project_dir = os.getcwd()
    else:
        project_dir = os.path.abspath(name)
    
    if not os.path.exists(project_dir):
        debugger.log_error(f"Project directory not found: {project_dir}")
        raise typer.Exit(1)
    
    config = load_config(project_dir, debugger)
    
    if port is not None:
        config['server']['port'] = port
        debugger.log_info(f"[dim]Port overridden to:[/] [cyan]{port}[/]")
    if host is not None:
        config['server']['host'] = host
        debugger.log_info(f"[dim]Host overridden to:[/] [cyan]{host}[/]")
    if http_port is not None:
        config['http_server']['port'] = http_port
        debugger.log_info(f"[dim]HTTP port overridden to:[/] [cyan]{http_port}[/]")
    if no_http:
        config['http_server']['enabled'] = False
        debugger.log_info("[dim]HTTP server disabled[/]")
    if verbose_http:
        config['http_server']['silent'] = False
        debugger.log_info("[dim]HTTP server logging enabled[/]")
        
    start_development_server(config, project_dir, hot_reload, debugger)

@app.command()
def new(
    name: Optional[str] = typer.Argument(None, help="New project name"),
    port: int = typer.Option(1337, "--port", "-p", help="Default server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="Default server host"),
    http_port: int = typer.Option(8000, "--http-port", help="Default HTTP server port"),
    template: str = typer.Option("default", "--template", "-t", help="Template to use for initialization")
):
    """
    Create new Quillion project
    """
    # Display banner with current debugger settings
    debugger.display_banner()
    
    if name is None:
        debugger.log_error("Project name is required")
        raise typer.Exit(1)
    
    # Create new project directory
    project_dir = os.path.abspath(name)
    os.makedirs(project_dir, exist_ok=True)
    
    config_path = os.path.join(project_dir, "quillion.toml")
    
    if os.path.exists(config_path):
        debugger.log_warning("quillion.toml already exists in this directory")
        if not typer.confirm("Overwrite existing config?"):
            return
    
    # Context for templates
    context = {
        'project_name': name,
        'port': port,
        'host': host,
        'http_port': http_port,
        'websocket_addr': f"ws://{host}:{port}",
        'App_name': name.capitalize()
    }
    
    # Define templates directory (use package directory for PyPI compatibility)
    templates_dir = Path(__file__).parent / ".templates"
    
    # Check if templates directory exists
    if not templates_dir.exists():
        debugger.log_error(f"Templates directory not found: {templates_dir}")
        raise typer.Exit(1)
    
    # Process all templates and copy non-template files
    process_templates_and_copy_files(project_dir, context, templates_dir, debugger)
    
    debugger.log_success(f"Project '[cyan]{name}[/]' created in [cyan]{project_dir}[/]")
    debugger.log_info(f"Run with: [cyan]q run {name}[/]")

@app.command()
def init(
    name: Optional[str] = typer.Argument(None, help="Project name (default: current directory)"),
    port: int = typer.Option(1337, "--port", "-p", help="Default server port"),
    host: str = typer.Option("127.0.0.1", "--host", help="Default server host"),
    http_port: int = typer.Option(8000, "--http-port", help="Default HTTP server port")
):
    """
    Initialize Quillion project in existing directory
    """
    debugger.display_banner()
    
    if name is None:
        project_dir = os.getcwd()
        project_name = os.path.basename(project_dir)
    else:
        project_dir = os.path.abspath(name)
        project_name = name
        os.makedirs(project_dir, exist_ok=True)
    
    config_path = os.path.join(project_dir, "quillion.toml")
    
    if os.path.exists(config_path):
        debugger.log_warning("quillion.toml already exists in this directory")
        if not typer.confirm("Overwrite existing config?"):
            return
    
    # Context for templates
    context = {
        'project_name': project_name,
        'port': port,
        'host': host,
        'http_port': http_port,
        'websocket_addr': f"ws://{host}:{port}",
        'App_name': project_name.capitalize()
    }
    
    # Define templates directory
    templates_dir = Path(__file__).parent / ".templates"
    
    if not templates_dir.exists():
        debugger.log_error(f"Templates directory not found: {templates_dir}")
        raise typer.Exit(1)
    
    # Process templates
    process_templates_and_copy_files(project_dir, context, templates_dir, debugger)
    
    debugger.log_success(f"Project '[cyan]{project_name}[/]' initialized in [cyan]{project_dir}[/]")

if __name__ == "__main__":
    app()