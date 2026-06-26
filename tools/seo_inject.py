#!/usr/bin/env python3
"""Post-process marimo WASM export to inject SEO meta tags, JSON-LD, and Open Graph.

Usage: python tools/seo_inject.py site/index.html
"""
import sys
import re
from pathlib import Path

URL = "https://kompress.vaked.dev"
TITLE = "Asymmetric Loss Modulation Resolves the Voting Ensemble Paradox"
DESCRIPTION = (
    "Interactive research paper: multi-checkpoint voting ensembles collapse to the "
    "weakest voter under k-of-N drop voting. The 3.0x heavy false-eviction penalty "
    "on critical-syntactic tokens resolves this. kompress-v8 production model, "
    "149M-param dual-head ModernBERT, trained via C3 self-distillation."
)
AUTHOR = "Lodri Peter"
IMAGE = f"{URL}/og-image.png"
DATE = "2026-06-25"

SEO_META = f"""    <meta name="description" content="{DESCRIPTION}" />
    <meta name="author" content="{AUTHOR}" />
    <link rel="canonical" href="{URL}" />

    <!-- Open Graph -->
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="kompress" />
    <meta property="og:url" content="{URL}" />
    <meta property="og:title" content="{TITLE}" />
    <meta property="og:description" content="{DESCRIPTION}" />
    <meta property="og:image" content="{IMAGE}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:locale" content="en_US" />
    <meta property="article:published_time" content="{DATE}" />
    <meta property="article:author" content="{AUTHOR}" />
    <meta property="article:tag" content="context-pruning" />
    <meta property="article:tag" content="ensemble-learning" />
    <meta property="article:tag" content="modernbert" />
    <meta property="article:tag" content="loop-engineering" />
    <meta property="article:tag" content="open-science" />

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@peetpedro" />
    <meta name="twitter:title" content="{TITLE}" />
    <meta name="twitter:description" content="{DESCRIPTION}" />
    <meta name="twitter:image" content="{IMAGE}" />

    <!-- JSON-LD Structured Data -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "ScholarlyArticle",
      "name": "{TITLE}",
      "description": "{DESCRIPTION}",
      "url": "{URL}",
      "datePublished": "{DATE}",
      "author": {{
        "@type": "Person",
        "name": "{AUTHOR}"
      }},
      "about": [
        {{"@type": "Thing", "name": "context-pruning"}},
        {{"@type": "Thing", "name": "ensemble-learning"}},
        {{"@type": "Thing", "name": "learned-compression"}}
      ],
      "publisher": {{
        "@type": "Organization",
        "name": "vaked"
      }},
      "isPartOf": {{
        "@type": "WebSite",
        "name": "kompress",
        "url": "{URL}"
      }},
      "mainEntity": {{
        "@type": "SoftwareApplication",
        "name": "kompress-v8",
        "url": "https://huggingface.co/PeetPedro/kompress-v8",
        "applicationCategory": "MachineLearningModel",
        "operatingSystem": "Linux"
      }}
    }}
    </script>"""


def inject_seo(html: str) -> str:
    """Inject SEO meta tags after <title> tag."""
    # Replace the basic description meta with full SEO block
    html = re.sub(
        r'<meta name="description" content="[^"]*" />',
        "",
        html,
    )

    # Insert SEO block after </title>
    html = html.replace("</title>", f"</title>\n{SEO_META}", 1)

    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python seo_inject.py <path/to/index.html>")
        sys.exit(1)

    path = Path(sys.argv[1])
    html = path.read_text()
    html = inject_seo(html)
    path.write_text(html)
    print(f"SEO meta tags injected into {path}")


if __name__ == "__main__":
    main()
