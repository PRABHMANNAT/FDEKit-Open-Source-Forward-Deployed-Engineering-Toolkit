# Shell completion

FDEKit uses Typer's built-in shell completion to suggest commands and options when you
press Tab. Completion is available after the `fdekit` command is installed and visible
on `PATH`.

## Prerequisites

Activate the virtual environment where FDEKit is installed, then confirm both the command
and completion options are available:

```console
fdekit --version
fdekit --help
```

The help output should list `--show-completion` and `--install-completion`. Run completion
commands directly inside the shell you want to configure because Typer detects the current
shell automatically.

## Try completion for the current session

Preview the generated script before loading it:

```console
fdekit --show-completion
```

Load it only in the current shell session:

| Shell | Temporary activation |
| --- | --- |
| Bash | `eval "$(fdekit --show-completion)"` |
| Zsh | `eval "$(fdekit --show-completion)"` |
| Fish | `fdekit --show-completion \| source` |
| Windows PowerShell or PowerShell 7 | `fdekit --show-completion \| Out-String \| Invoke-Expression` |

This does not persist after the shell exits. Test it by typing `fdekit sc` and pressing
Tab; the command should complete to `fdekit scan`.

The PowerShell commands above were exercised end to end with Windows PowerShell and
PowerShell 7. Bash, Zsh, and Fish script generation was verified with the project's
installed Typer 0.27.2; those shells were not available in the Windows validation
environment for interactive Tab testing.

## Install completion persistently

Typer can detect the current shell and install its generated script:

```console
fdekit --install-completion
```

The command prints the file it changed or created. Record that path, restart the shell,
and test `fdekit sc` followed by Tab. With Typer 0.27.2, the usual generated files are:

| Shell | Completion file or profile |
| --- | --- |
| Bash | `~/.bash_completions/fdekit.sh`, sourced from `~/.bashrc` |
| Zsh | `~/.zfunc/_fdekit`, loaded through `~/.zshrc` |
| Fish | `~/.config/fish/completions/fdekit.fish` |
| Windows PowerShell / PowerShell 7 | The profile path printed by the installer |

Typer 0.27.2's PowerShell installer also changes the current user's execution policy to
`Unrestricted` before appending completion code to the profile. If that policy change is
not appropriate for your environment, keep using temporary activation or install the
generated block manually with clear markers:

```powershell
$profileDirectory = Split-Path -Parent $PROFILE
New-Item -ItemType Directory -Force $profileDirectory | Out-Null
Add-Content -Path $PROFILE -Value "`n# BEGIN FDEKit completion"
fdekit --show-completion | Add-Content -Path $PROFILE
Add-Content -Path $PROFILE -Value "# END FDEKit completion"
```

Review `$PROFILE` before editing it, especially on managed systems.

## Disable or remove completion

There is no FDEKit uninstall-completion command. Undo only the changes associated with
FDEKit, then restart the shell:

- Bash: delete `~/.bash_completions/fdekit.sh` and remove its `source` line from
  `~/.bashrc`.
- Zsh: delete `~/.zfunc/_fdekit`. Remove Typer-added `fpath`, `compinit`, or `zstyle`
  lines from `~/.zshrc` only when no other completion uses them.
- Fish: delete `~/.config/fish/completions/fdekit.fish`.
- PowerShell: remove the block that registers completion for `fdekit` and references
  `_FDEKIT_COMPLETE` from the profile printed during installation. If you used the
  marked manual setup, remove everything between its BEGIN and END comments.

Back up a shared shell profile before editing it. Removing completion does not uninstall
FDEKit.

## Troubleshooting

- If `fdekit` is not found, activate the environment where it is installed or add that
  environment's executable directory to `PATH`.
- If shell detection fails, run `fdekit --show-completion` directly from the target shell
  instead of through an editor task, wrapper, or redirected parent process.
- If installed completion is not active, restart the shell and verify that the generated
  file exists and the relevant profile loads it.
- In PowerShell, ensure `PSReadLine` is available and inspect the effective policy with
  `Get-ExecutionPolicy -List`; follow your organization's policy rather than weakening it.
- Re-run `fdekit --help` after upgrading Typer. Generated locations and installation
  behavior can change between dependency versions.
