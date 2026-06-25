{
  description = "longrun-eval-kompress — Voting Ensemble Paradox research";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    # Formatting & linting
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # Pre-commit hooks
    pre-commit-hooks = {
      url = "github:cachix/pre-commit-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, treefmt-nix, pre-commit-hooks }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # ── Python ──────────────────────────────────────────
        python = pkgs.python312;

        pythonEnv = python.withPackages (ps: with ps; [
          marimo numpy matplotlib ipykernel
          sumy nltk
        ]);

        pipExtra = [ "mcp" "llmlingua" ];

        # ── LaTeX ───────────────────────────────────────────
        texlive = pkgs.texlive.combined.scheme-basic.extend (drv: {
          extraPackages = with pkgs.texlive; [
            amsmath amssymb amscls mathtools
            booktabs multirow array
            natbib hyperref geometry
            xcolor graphicx url latexmk
          ];
        });

        # ── treefmt (module eval) ───────────────────────────
        treefmtEval = treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.nixpkgs-fmt.enable = true;
          programs.black.enable = true;
          programs.jsonfmt.enable = true;
          programs.yamlfmt.enable = true;
          programs.mdformat.enable = true;
          settings.global.excludes = [
            "site/assets/*"
            "flake.lock"
            "*.lock"
          ];
        };

        # ── Pre-commit hooks ────────────────────────────────
        preCommitEval = pre-commit-hooks.lib.${system}.run {
          src = self;
          hooks = {
            treefmt.enable = true;
            treefmt.package = treefmtEval.config.programs.treefmt.package;

            trailing-whitespace.enable = true;
            end-of-file-fixer.enable = true;
            check-merge-conflict.enable = true;
            detect-private-keys.enable = true;

            ruff.enable = true;
            ruff.args = [ "--fix" ];
          };
        };

      in {
        # ── Dev shell ─────────────────────────────────────
        devShells.default = pkgs.mkShell {
          name = "longrun-eval-kompress";

          packages = [
            pythonEnv
            texlive
            pkgs.task pkgs.git pkgs.gh pkgs.curl pkgs.jq

            # treefmt wrapper
            treefmtEval.config.programs.treefmt.package
          ];

          shellHook = ''
            ${preCommitEval.config.installationScript}

            echo ""
            echo "  longrun-eval-kompress dev shell"
            echo "  Python $(python3 --version | cut -d' ' -f2)  |  task $(task --version 2>/dev/null | awk '{print $2}')"
            echo ""
            echo "  task --list          all commands"
            echo "  task paper:build     compile PDF"
            echo "  task site:build      marimo -> WASM"
            echo "  task ci              all checks"
            echo "  treefmt              format everything"
            echo "  pre-commit run -a    run hooks manually"
            echo ""

            # Install Python packages not in nixpkgs
            if [ ! -f .venv-stamp ] || [ .venv-stamp -ot flake.nix ]; then
              echo "Installing extra Python packages: ${builtins.concatStringsSep " " pipExtra}"
              pip install --quiet ${pkgs.lib.concatStringsSep " " pipExtra} 2>/dev/null || true
              touch .venv-stamp
            fi
          '';
        };

        # ── Apps ──────────────────────────────────────────
        apps = {
          nb-edit.type = "app";
          nb-edit.program = "${pythonEnv}/bin/marimo";
          nb-edit.args = [ "edit" "notebook.py" ];

          nb-run.type = "app";
          nb-run.program = "${pythonEnv}/bin/marimo";
          nb-run.args = [ "run" "notebook.py" ];

          paper.type = "app";
          paper.program = "${texlive}/bin/latexmk";
          paper.args = [ "-pdf" "-cd" "paper/main.tex" ];
        };

        # ── Checks (CI / nix flake check) ──────────────────
        checks = {
          formatting = treefmtEval.config.build.devShell;
          pre-commit = preCommitEval;
        };
      }
    );
}
