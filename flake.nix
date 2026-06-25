{
  description = "longrun-eval-kompress — Voting Ensemble Paradox research";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python312;

        pythonEnv = python.withPackages (ps: with ps; [
          marimo
          numpy
          matplotlib
          ipykernel
        ]);

        texlive = pkgs.texlive.combined.scheme-basic.extend (drv: {
          extraPackages = with pkgs.texlive; [
            amsmath
            amssymb
            amscls
            mathtools
            booktabs
            multirow
            array
            natbib
            hyperref
            geometry
            xcolor
            graphicx
            url
            latexmk
          ];
        });

      in {
        devShells.default = pkgs.mkShell {
          name = "longrun-eval-kompress";

          packages = [
            pythonEnv
            texlive
            pkgs.task
            pkgs.git
            pkgs.curl
            pkgs.jq
          ];

          shellHook = ''
            echo "┌─────────────────────────────────────────────┐"
            echo "│  longrun-eval-kompress dev shell             │"
            echo "│  Python $(python --version | cut -d' ' -f2)   │"
            echo "│  LaTeX $(latexmk --version 2>/dev/null | head -1 | awk '{print $4}')"
            echo "│  task $(task --version 2>/dev/null | awk '{print $2}')"
            echo "│                                             │"
            echo "│  task --list       see all commands         │"
            echo "│  task paper:build  compile PDF              │"
            echo "│  task site:build   export marimo → WASM     │"
            echo "│  task ci           run all checks           │"
            echo "└─────────────────────────────────────────────┘"

            # Install Python packages not in nixpkgs
            if [ ! -f .venv-stamp ] || [ .venv-stamp -ot flake.nix ]; then
              echo "Installing additional Python packages..."
              pip install --quiet mcp sumy nltk llmlingua 2>/dev/null || true
              touch .venv-stamp
            fi
          '';
        };
      }
    );
}
