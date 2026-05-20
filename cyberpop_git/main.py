"""
Cyberpop Git Main CLI Entry Point
Handles routing of commands: config, init, push, and summary.
Implements beautiful custom cyberpunk help screens and interactive loops.
"""

import sys
import argparse
import os
from pathlib import Path

def sanitize_env():
    """Removes local custom certificate bundle overrides from the environment to prevent MITM interception."""
    os.environ.pop("REQUESTS_CA_BUNDLE", None)
    os.environ.pop("CURL_CA_BUNDLE", None)

from cyberpop_git.ui import (
    print_logo,
    print_success,
    print_error,
    print_info,
    print_warning,
    print_commit_panel,
    render_table,
    CyberSpinner,
    console,
    ar,
    copy_to_clipboard
)
from cyberpop_git.config import (
    load_config,
    save_config,
    get_api_key,
    set_api_key,
    update_setting,
    get_active_model
)
import cyberpop_git.git_manager as git
import cyberpop_git.ai_service as ai
import cyberpop_git.templates as templates

from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

def show_custom_help():
    """Renders a mind-blowing Cyberpunk CLI help manual."""
    print_logo()
    
    manual = Text()
    manual.append("\n" + ar("⚡ SYSTEM OPERATIONAL PROTOCOLS ⚡") + "\n", style="bold #ffe600")
    
    headers = ["Command", "Description / Protocol", "Usage Example"]
    rows = [
        [
            "[bold #ff007f]config[/bold #ff007f]",
            "Configure API keys, models, and proxy settings securely.",
            "cyberpop-git config --key KEY"
        ],
        [
            "[bold #00f0ff]init[/bold #00f0ff]",
            "Analyze project environment and auto-generate .gitignore.",
            "cyberpop-git init"
        ],
        [
            "[bold #39ff14]push[/bold #39ff14]",
            "Analyze local diff, generate smart commit message, and push.",
            "cyberpop-git push"
        ],
        [
            "[bold #8a2be2]summary[/bold #8a2be2]",
            "Synthesize daily progress into a structured standup report.",
            "cyberpop-git summary"
        ]
    ]
    render_table("CYBERPOP CLI OPERATIONS MATRIX", headers, rows)
    
    console.print(Panel(
        ar("[bold #ffe600]Operational Tip:[/bold #ffe600] You can run [bold #00f0ff]cyberpop-git push[/bold #00f0ff] directly to stage files.\n"
        "The system will automatically prompt you to stage modifications if [bold #00f0ff]'git add'[/bold #00f0ff] was not executed!"),
        border_style="bold #ffe600",
        title=ar("[bold #ffe600]▼ Operational Intelligence ▼[/bold #ffe600]")
    ))

def handle_config(args):
    """Handles the 'config' command."""
    if args.show:
        config = load_config()
        # Mask API keys (decrypting first to mask the actual plaintext key safely)
        gemini_key = get_api_key("gemini")
        masked_gemini = gemini_key[:6] + "..." + gemini_key[-4:] if len(gemini_key) > 10 else "Not Configured"
        
        openai_key = get_api_key("openai")
        masked_openai = openai_key[:6] + "..." + openai_key[-4:] if len(openai_key) > 10 else "Not Configured"
        
        proxy_val = config.get("proxy", "")
        masked_proxy = f"[bold #ffe600]{proxy_val}[/bold #ffe600]" if proxy_val else "[bold #ff007f]✘ Inactive[/bold #ff007f]"
        
        headers = ["Parameter", "Active Configuration Value"]
        rows = [
            ["Active AI Provider", f"[bold #00f0ff]{config.get('provider')}[/bold #00f0ff]"],
            ["Gemini Model", config.get("gemini_model")],
            ["OpenAI Model", config.get("openai_model")],
            ["Gemini API Key", f"[bold #39ff14]{masked_gemini}[/bold #39ff14]"],
            ["OpenAI API Key", f"[bold #ff007f]{masked_openai}[/bold #ff007f]"],
            ["Proxy Server", masked_proxy]
        ]
        render_table("ACTIVE COGNITIVE ENGINE CONFIGURATION", headers, rows)
        return

    changes_made = False
    
    if args.key:
        provider = args.provider or load_config().get("provider", "gemini")
        set_api_key(args.key, provider)
        print_success(f"API key for [bold]{provider}[/bold] has been securely stored in the local vault.", "Security Vault Updated")
        changes_made = True
        
    if args.provider:
        if args.provider not in ["gemini", "openai"]:
            print_error("Unsupported AI provider. Select 'gemini' or 'openai'.", "Configuration Failure")
            return
        update_setting("provider", args.provider)
        print_success(f"Primary operational routing updated to [bold #ffe600]{args.provider}[/bold #ffe600].", "Routing Channel Updated")
        changes_made = True
        
    if args.model:
        config = load_config()
        active_provider = args.provider or config.get("provider", "gemini")
        if active_provider == "gemini":
            update_setting("gemini_model", args.model)
        else:
            update_setting("openai_model", args.model)
        print_success(f"Active neural model set to [bold #ffe600]{args.model}[/bold #ffe600].", "Model Updated")
        changes_made = True

    if args.proxy is not None:
        proxy_val = args.proxy.strip()
        if proxy_val.lower() in ["none", "clear", ""]:
            update_setting("proxy", "")
            print_success("Network proxy server deactivated successfully.", "Network Settings Updated")
        else:
            update_setting("proxy", proxy_val)
            print_success(f"Network proxy server successfully routed through [bold #ffe600]{proxy_val}[/bold #ffe600].", "Network Settings Updated")
        changes_made = True

    if not changes_made:
        print_warning("No changes made. Execute [bold]cyberpop-git config -h[/bold] for instructions.", "No Operations Triggered")

def handle_init():
    """Handles the 'init' command to scan stack and write .gitignore."""
    print_info("Scanning codebase for technology stack signature...", "Environment Scan Initiated")
    
    if not git.is_git_repository():
        print_warning("No active Git repository detected. Initializing a new repository...", "Git Repository Missing")
        try:
            git.run_git_cmd(["init"])
            print_success("Empty Git repository successfully initialized locally.", "Repository Created")
        except git.GitError as e:
            print_error(f"Failed to initialize Git repository: {str(e)}", "Repository Initialization Failed")
            return
            
    detected = templates.detect_languages(".")
    
    if detected:
        tech_list = ", ".join(f"[bold #ffe600]{t}[/bold #ffe600]" for t in detected)
        print_success(f"Detected project technology signatures: {tech_list}", "Environment Identified")
    else:
        print_info("Unable to identify specific technology signatures. Using fallback general template.", "General Environment Profile")
        
    gitignore_content = templates.generate_gitignore_content(detected)
    gitignore_path = Path(".") / ".gitignore"
    
    # Check if .gitignore already exists
    if gitignore_path.exists():
        console.print()
        response = console.input(
            ar("[bold #ff007f]⚠ A .gitignore file already exists. Do you want to overwrite it? (y/N): [/bold #ff007f]")
        ).strip().lower()
        if response not in ["y", "yes"]:
            print_info("Operation aborted. Existing .gitignore remains unchanged.", "No Changes Applied")
            return

    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        print_success("Premium, optimized .gitignore file successfully generated and saved!", "gitignore Configured")
    except Exception as e:
        print_error(f"Failed to write .gitignore file: {str(e)}", "File IO Failure")

def handle_push():
    """Handles the core 'push' command with interactive AI confirmation loop."""
    if not git.is_git_repository():
        print_error("This directory is not an active Git repository. Run [bold]cyberpop-git init[/bold] first.", "Workspace Verification Error")
        return

    # Check if staged changes exist
    if not git.has_staged_files():
        print_warning("No staged files detected in the Git staging area.", "Staging Area Empty")
        
        status_short = git.get_status_short()
        if status_short:
            console.print(ar("[bold #00f0ff]Current unstaged modifications in workspace:[/bold #00f0ff]"))
            console.print(status_short)
            console.print()
            
            response = console.input(
                ar("[bold #ff007f]🗲 Do you want to stage all local modifications (git add .)? (Y/n): [/bold #ff007f]")
            ).strip().lower()
            
            if response in ["y", "yes", ""]:
                try:
                    with CyberSpinner("Staging all modifications into Git cache...", "#8a2be2"):
                        git.stage_all_files()
                    print_success("All local modifications successfully staged.", "Staging Completed")
                except git.GitError as e:
                    print_error(f"Failed to stage files: {str(e)}", "Staging Operation Failure")
                    return
            else:
                print_info("Staging cancelled. Please stage files manually using 'git add' and retry.", "Operation Paused")
                return
        else:
            print_info("Workspace is clean. There are no changes to commit or push.", "Sync Status: OK")
            return

    # Now we have staged files, extract the diff
    try:
        diff_text = git.get_staged_diff()
        if not diff_text.strip():
            print_info("Staged diff is empty. Please verify your staged changes.", "Empty Delta")
            return
    except git.GitError as e:
        print_error(f"Failed to extract staged diff: {str(e)}", "Git Analysis Failure")
        return

    # AI message generation loop
    commit_msg = ""
    while True:
        try:
            with CyberSpinner("🤖 AI is reading and analyzing codebase changes...", "#00f0ff"):
                commit_msg = ai.generate_commit_message(diff_text)
        except ai.AIServiceError as e:
            print_error(str(e), "AI Service Connection Failure")
            return
        
        print_commit_panel(commit_msg)
        
        # Confirmation menu
        console.print(ar("[bold #00f0ff]⚡ Operational Decision Node:[/bold #00f0ff]"))
        console.print(ar("[1] [bold #39ff14]Commit & Push immediately[/bold #39ff14] [Default - Press Enter]"))
        console.print(ar("[2] [bold #ffe600]Edit commit message manually[/bold #ffe600]"))
        console.print(ar("[3] [bold #ff007f]Regenerate commit message with AI[/bold #ff007f]"))
        console.print(ar("[4] [bold #8a2be2]Cancel operation entirely[/bold #8a2be2]"))
        console.print()
        
        choice = console.input(ar("[bold #ffe600]▼ Enter selection [1-4]: [/bold #ffe600]")).strip()
        
        if choice in ["", "1"]:
            # Commit and push
            break
        elif choice == "2":
            # Edit manual
            commit_msg = console.input(ar("\n[bold #00f0ff]✎ Enter your custom commit message: [/bold #00f0ff]")).strip()
            if not commit_msg:
                print_warning("Commit message cannot be empty. Returning to decision node.", "Validation Warning")
                continue
            break
        elif choice == "3":
            # Regenerate loop
            print_info("Re-contacting neural network to generate a new message...", "API Request Dispatched")
            continue
        elif choice == "4":
            print_info("Push protocol aborted. Modifications remain in Git staging.", "Operation Aborted")
            return
        else:
            print_warning("Invalid option selected. Please choose a number from 1 to 4.", "Input Warning")

    # Commit and Push execution
    try:
        with CyberSpinner("Recording commit entry inside local repository...", "#ffe600"):
            git.commit(commit_msg)
        print_success("Commit successfully registered.", "Local Commit Completed")
    except git.GitError as e:
        print_error(f"Commit operation failed: {str(e)}", "Git Commit Failure")
        return

    try:
        active_branch = git.get_active_branch()
        with CyberSpinner(f"Uploading local commits to remote branch [bold #ff007f]{active_branch}[/bold #ff007f] (git push)...", "#ff007f"):
            git.push()
        print_success("Code changes successfully pushed to the remote repository!", "Push Operation Completed")
    except git.GitError as e:
        print_error(f"Push operation failed: {str(e)}\n\n(Note: Commit was created locally. You can push manually later.)", "Git Push Failure")

def handle_summary():
    """Handles the 'summary' command to generate Daily Standup Report."""
    if not git.is_git_repository():
        print_error("This directory is not an active Git repository. Run [bold]cyberpop-git init[/bold] first.", "Workspace Verification Error")
        return

    with CyberSpinner("Extracting Git modification logs...", "#8a2be2"):
        commits = git.get_today_commits()

    if not commits:
        print_info(
            "No commits found for today in this repository.\n"
            "The system only analyzes today's commits to generate a precise standup report.",
            "Today's Log Empty"
        )
        return

    # Render commits table first
    headers = ["Commit Hash", "Commit Header / Subject"]
    rows = []
    for commit_line in commits:
        # Split hash from message
        parts = commit_line.rsplit(" (", 1)
        msg = parts[0]
        ref = parts[1].replace(")", "") if len(parts) > 1 else "Unknown"
        rows.append([f"[bold #ff007f]{ref}[/bold #ff007f]", msg])
        
    render_table("TODAY'S TEMPORAL COMMITS RECORD", headers, rows)

    try:
        with CyberSpinner("AI is synthesizing and structuring daily standup report...", "#00f0ff"):
            report = ai.generate_daily_standup(commits)
    except ai.AIServiceError as e:
        print_error(str(e), "Report Synthesis Failure")
        return

    # Display the final gorgeous report using rich markdown
    console.print()
    report_panel = Panel(
        Markdown(ar(report)),
        title=f"[bold #39ff14]★ {ar('DAILY STANDUP REPORT')} ★[/bold #39ff14]",
        border_style="bold #39ff14",
        padding=(1, 3),
        expand=True
    )
    console.print(report_panel)
    # Automatically copy the generated daily standup report to clipboard
    copied = copy_to_clipboard(report)
    if copied:
        print_success("Daily standup report successfully generated and copied to clipboard!", "Synthesis & Copy Completed")
    else:
        print_success("Daily standup report successfully generated and ready to share.", "Synthesis Completed")

def main():
    """Main CLI driver."""
    sanitize_env()
    # Custom help trigger
    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        show_custom_help()
        if len(sys.argv) == 1:
            console.print()
            console.print(ar("[bold #ffe600]▼ Press ENTER to exit and release system protocols ▼[/bold #ffe600]"))
            input()
        sys.exit(0)
        
    parser = argparse.ArgumentParser(description="Cyberpop AI Git Automation CLI", add_help=False)
    subparsers = parser.add_subparsers(dest="command")
    
    # Subcommand 'config'
    config_parser = subparsers.add_parser("config", add_help=False)
    config_parser.add_argument("--key", type=str, help="Set API Key locally.")
    config_parser.add_argument("--provider", type=str, choices=["gemini", "openai"], help="Set active AI Provider.")
    config_parser.add_argument("--model", type=str, help="Set active model name.")
    config_parser.add_argument("--proxy", type=str, help="Set HTTP/HTTPS proxy URL (or 'none' to disable).")
    config_parser.add_argument("--show", action="store_true", help="Show current system configuration.")
    
    # Subcommand 'init'
    subparsers.add_parser("init", add_help=False)
    
    # Subcommand 'push'
    subparsers.add_parser("push", add_help=False)
    
    # Subcommand 'summary'
    subparsers.add_parser("summary", add_help=False)
    
    try:
        args, unknown = parser.parse_known_args()
    except Exception as e:
        print_error(f"Arguments parsing failure: {str(e)}", "CLI Parser Error")
        sys.exit(1)
        
    try:
        if args.command == "config":
            handle_config(args)
        elif args.command == "init":
            handle_init()
        elif args.command == "push":
            handle_push()
        elif args.command == "summary":
            handle_summary()
        else:
            print_error(f"Unknown operational protocol '{args.command}'. Execute without arguments to view helper manual.", "System Error")
            sys.exit(1)
    except KeyboardInterrupt:
        console.print()
        print_warning("Operation aborted by user. Deactivating system protocols.", "Operation Cancelled")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected system exception: {str(e)}", "Operational Failure")
        sys.exit(1)

if __name__ == "__main__":
    main()
