import sys
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.progress import track

console = Console()
BASE_URL = "http://localhost:8000"

def check_server():
    try:
        requests.get(f"{BASE_URL}/docs", timeout=2)
        return True
    except requests.ConnectionError:
        return False

def show_banner():
    banner = """
    ███████╗███████╗███████╗ █████╗ ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
    ██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
    █████╗  ███████╗███████╗███████║███████╗█████╗  ███████║██████╔╝██║     ███████║
    ██╔══╝  ╚════██║╚════██║██╔══██║╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
    ███████╗███████║███████║██║  ██║███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
    ╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
    """
    console.print(Panel(banner, style="bold cyan", title="Distributed Search Engine"))

def index_document():
    doc_id = Prompt.ask("[bold yellow]Enter Document ID")
    content = Prompt.ask("[bold yellow]Enter Document Content")
    author = Prompt.ask("[bold yellow]Enter Author Name (Optional)", default="Unknown")

    try:
        payload = {
            "id": doc_id,
            "content": content,
            "metadata": {"author": author}
        }
        res = requests.post(f"{BASE_URL}/index", json=payload)
        res.raise_for_status()
        console.print(f"[bold green]✓ Document '{doc_id}' indexed successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Failed to index document: {e}[/bold red]")

def search_documents():
    query = Prompt.ask("[bold cyan]Enter Search Query[/bold cyan]")
    try:
        res = requests.post(f"{BASE_URL}/search", json={"query": query, "limit": 10})
        if res.status_code == 200:
            data = res.json()
            hits = data.get("hits", 0)
            
            console.print(f"\n[bold green]Found {hits} results for '{query}'[/bold green]")
            
            if hits > 0:
                table = Table(title="Search Results", border_style="blue")
                table.add_column("Rank", justify="center", style="cyan")
                table.add_column("Score", justify="right", style="green")
                table.add_column("Doc ID", justify="left", style="magenta")
                table.add_column("Content Preview", justify="left", style="white")
                
                for idx, result in enumerate(data.get("results", [])):
                    score = f"{result['score']:.4f}"
                    content = result['content']
                    
                    # Convert [[term]] to Rich tags
                    content = content.replace("[[", "[bold cyan]").replace("]]", "[/bold cyan]")
                    
                    table.add_row(str(idx + 1), score, result['id'], content)
                    
                console.print(table)
        else:
            console.print(f"[bold red]✗ Server returned status: {res.status_code}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]✗ Search failed: {e}[/bold red]")

def view_stats():
    try:
        res = requests.get(f"{BASE_URL}/stats")
        res.raise_for_status()
        stats = res.json()
        
        table = Table(title="EssaSearch Engine Stats")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")
        table.add_row("Total Documents", str(stats["total_documents"]))
        table.add_row("Total Unique Terms", str(stats["total_terms"]))
        table.add_row("Documents in Memory", str(stats.get("memory_documents", 0)))
        table.add_row("Documents on Disk", str(stats.get("disk_documents", 0)))
        table.add_row("Active Disk Segments", str(stats.get("active_segments", 0)))
        
        cache_stats = stats.get("cache_stats", {})
        if cache_stats:
            hit_ratio = f"{cache_stats.get('hit_ratio', 0) * 100:.1f}%"
            table.add_row("Cache Hit Ratio", f"{hit_ratio} ({cache_stats.get('hits')} hits, {cache_stats.get('misses')} misses)")
        
        console.print(table)
    except Exception as e:
         console.print(f"[bold red]✗ Failed to fetch stats: {e}[/bold red]")

def flush_index():
    try:
        res = requests.post(f"{BASE_URL}/flush")
        res.raise_for_status()
        console.print("[bold green]✓ Memory index successfully flushed to disk![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Flush failed: {e}[/bold red]")

def merge_segments():
    try:
        res = requests.post(f"{BASE_URL}/merge")
        res.raise_for_status()
        console.print("[bold green]✓ Disk segments successfully merged into a single optimized segment![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Merge failed: {e}[/bold red]")

def cluster_backup():
    filename = Prompt.ask("[bold yellow]Enter backup filename (e.g., my_cluster_backup.zip)[/bold yellow]")
    try:
        res = requests.post(f"{BASE_URL}/backup", json={"filename": filename})
        if res.status_code == 200 and res.json().get("status") == "success":
            console.print(f"[bold green]✓ {res.json()['message']}[/bold green]")
        else:
            console.print(f"[bold red]✗ Backup failed: {res.json().get('message')}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]✗ Backup failed: {e}[/bold red]")

def cluster_restore():
    filename = Prompt.ask("[bold yellow]Enter backup filename to restore (e.g., my_cluster_backup.zip)[/bold yellow]")
    confirm = Prompt.ask("[bold red]WARNING: This will overwrite current data. Continue? (y/n)[/bold red]", choices=["y", "n"])
    if confirm == 'y':
        try:
            res = requests.post(f"{BASE_URL}/restore", json={"filename": filename})
            if res.status_code == 200 and res.json().get("status") == "success":
                console.print(f"[bold green]✓ {res.json()['message']}[/bold green]")
            else:
                console.print(f"[bold red]✗ Restore failed: {res.json().get('message')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]✗ Restore failed: {e}[/bold red]")

def main():
    show_banner()
    if not check_server():
        console.print("[bold red]⚠ Cannot connect to EssaSearch server. Is it running on port 8000?[/bold red]")
        sys.exit(1)

    while True:
        console.print("\n[1] [cyan]Search Documents[/cyan]")
        console.print("[2] [yellow]Index New Document[/yellow]")
        console.print("[3] [magenta]View Engine Stats[/magenta]")
        console.print("[4] [blue]Flush Memory to Disk[/blue]")
        console.print("[5] [green]Merge Disk Segments (Optimize)[/green]")
        console.print("[6] [yellow]Backup Cluster[/yellow]")
        console.print("[7] [red]Restore Cluster from Backup[/red]")
        console.print("[8] [red]Exit[/red]")
        
        choice = Prompt.ask("Choose an action", choices=[str(i) for i in range(1, 9)])
        
        if choice == "1":
            search_documents()
        elif choice == "2":
            index_document()
        elif choice == "3":
            view_stats()
        elif choice == "4":
            flush_index()
        elif choice == "5":
            merge_segments()
        elif choice == "6":
            cluster_backup()
        elif choice == "7":
            cluster_restore()
        elif choice == "8":
            console.print("[bold green]Goodbye![/bold green]")
            break

if __name__ == "__main__":
    main()
