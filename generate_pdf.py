#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FEBUS Rulebook - Markdown to PDF Converter
Spojí všetky MD súbory do jedného PDF dokumentu so zachovaním pôvodného textu a formátovania
"""

import os
import re
import html
import base64
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
import markdown
import warnings
# Suppress the deprecation warning from WeasyPrint
warnings.filterwarnings('ignore', message='.*instantiateVariableFont.*')
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import datetime
import PyPDF2
import tempfile

class MarkdownToPDFConverter:
    def __init__(self):
        self.md_files = []
        self.toc_entries = []
        self.chapter_counter = 0
        self.section_counters = {}
        self.page_numbers = {}  # Store page numbers for anchors
        self.num_root_files = 0
        
    def collect_markdown_files(self) -> List[Tuple[str, Path]]:
        """Zozbiera všetky .md súbory a zoradí ich podľa číslovania"""
        root_files = []
        appendix_files = []
        
        # Hlavné súbory v root adresári
        for file in Path('.').glob('*.md'):
            if file.name not in ['README.md', 'CLAUDE.md', 'CHANGELOG.md'] \
                    and not file.name.startswith('FEBUS_smernica'):
                root_files.append((file.name, file))
        
        # Súbory v appendices
        appendices_dir = Path('appendices')
        if appendices_dir.exists():
            for file in appendices_dir.glob('*.md'):
                appendix_files.append((f"appendices/{file.name}", file))
        
        # Zoradiť podľa číslovania (01-, 02-, atď.)
        root_files.sort(key=lambda x: x[0])
        self.num_root_files = len(root_files)
        appendix_files.sort(key=lambda x: x[0])

        self.md_files = root_files + appendix_files
        return self.md_files
    
    def extract_headers_for_toc(self, content: str, file_name: str, chapter_num: int):
        """Extrahuje hlavičky pre obsah s číslovaním"""
        chapter_id = file_name.replace('.md', '').replace('/', '-')
        is_appendix = 'appendices' in file_name
        
        lines = content.split('\n')
        h2_counter = 0
        h3_counter = 0
        
        for line in lines:
            if line.startswith('#'):
                # Počet # určuje úroveň
                header_level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('#').strip()
                
                if header_text and header_level <= 2:  # Len h1, h2 do obsahu
                    # Generovať číslovanie pre TOC
                    if header_level == 1:
                        h2_counter = 0
                        h3_counter = 0
                        if is_appendix:
                            number = f"A{chapter_num - self.num_root_files}"
                        else:
                            number = f"{chapter_num}"
                    elif header_level == 2:
                        h2_counter += 1
                        h3_counter = 0
                        if is_appendix:
                            number = f"A{chapter_num - self.num_root_files}.{h2_counter}"
                        else:
                            number = f"{chapter_num}.{h2_counter}"
                    elif header_level == 3:
                        h3_counter += 1
                        if is_appendix:
                            number = f"A{chapter_num - self.num_root_files}.{h2_counter}.{h3_counter}"
                        else:
                            number = f"{chapter_num}.{h2_counter}.{h3_counter}"
                    else:
                        number = ""
                    
                    # Vytvoriť ID pre navigáciu
                    header_id = re.sub(r'[^\w\s-]', '', header_text.lower())
                    header_id = re.sub(r'[-\s]+', '-', header_id)
                    anchor = f"{chapter_id}-{header_id}"
                    
                    # Pridať číslovanie do TOC
                    numbered_text = f"{number}. {header_text}" if number else header_text
                    self.toc_entries.append((header_level, numbered_text, anchor))
    
    def generate_table_of_contents(self, with_page_numbers=False) -> str:
        """Vygeneruje HTML pre obsah"""
        toc_html = ['<div class="toc">']
        toc_html.append('<h1 class="toc-title">TABLE OF CONTENTS</h1>')
        toc_html.append('<div class="toc-content">')
        
        for level, title, anchor in self.toc_entries:
            # Create professional TOC entry
            page_num = ""
            if with_page_numbers and anchor in self.page_numbers:
                page_num = str(self.page_numbers[anchor])
            
            # Truncate very long titles
            display_title = title
            if len(title) > 85:  # Limit title length for better layout
                display_title = title[:82] + "..."
            
            indent_class = f'toc-level-{level}'
            toc_html.append(f'<div class="{indent_class}">')
            toc_html.append(f'  <div class="toc-line">')
            toc_html.append(f'    <span class="toc-text"><a href="#{anchor}">{display_title}</a></span>')
            toc_html.append(f'    <span class="toc-dots"></span>')
            toc_html.append(f'    <span class="toc-page">{page_num}</span>')
            toc_html.append(f'  </div>')
            toc_html.append(f'</div>')
        
        toc_html.append('</div>')
        toc_html.append('</div>')
        toc_html.append('<div class="page-break"></div>')
        
        return '\n'.join(toc_html)
    
    def convert_md_links_to_anchors(self, content: str, file_name: str) -> str:
        """Konvertuje odkazy na .md súbory na interné HTML kotvy

        Cesty v odkazoch sú relatívne k súboru, v ktorom sa nachádzajú (napr.
        appendices/01-glossary.md odkazuje na ../04-right-of-way.md), takže sa
        musia rozlíšiť voči adresáru zdrojového súboru (`file_name`) — nie voči
        surovej ceste z odkazu — inak vznikne kotva, ktorá v dokumente
        neexistuje (napr. '#..-04-right-of-way' namiesto '#04-right-of-way').
        """
        # Pattern pre markdown odkazy: [text](path/file.md) alebo [text](path/file.md#anchor)
        def replace_link(match):
            link_text = match.group(1)
            link_path = match.group(2)

            # Ak link nie je na .md súbor, nechaj ho tak
            if not '.md' in link_path:
                return match.group(0)

            # Rozdeliť cestu a kotvu ak existuje
            if '#' in link_path:
                file_part, anchor_part = link_path.split('#', 1)
            else:
                file_part, anchor_part = link_path, None

            # Rozlíšiť cestu voči adresáru zdrojového súboru
            resolved = os.path.normpath(os.path.join(os.path.dirname(file_name), file_part))
            chapter_id = resolved.replace('.md', '').replace(os.sep, '-').replace('/', '-')

            if anchor_part is not None:
                internal_anchor = f"#{chapter_id}-{anchor_part}"
            else:
                # Len súbor bez kotvy - odkazuj na začiatok kapitoly
                internal_anchor = f"#{chapter_id}"

            return f"[{link_text}]({internal_anchor})"

        # Regex pre markdown odkazy
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        return re.sub(pattern, replace_link, content)

    def convert_markdown_to_html(self, content: str, file_name: str, chapter_num: int) -> str:
        """Konvertuje markdown na HTML s pridaním ID a číslovania pre navigáciu"""
        # Najprv konvertuj .md odkazy na interné kotvy
        content = self.convert_md_links_to_anchors(content, file_name)

        # Inicializovať markdown konvertor
        md = markdown.Markdown(extensions=[
            'extra',        # tables, attr_list, def_list, footnotes, abbr, fenced_code
            'sane_lists',   # lepšie spracovanie zoznamov
            'smarty',       # inteligentné úvodzovky
            'toc'           # table of contents
            # Removed nl2br to avoid excessive line breaks
        ])

        # Konvertovať markdown na HTML
        html_content = md.convert(content)
        
        # Pridať ID a číslovanie k hlavičkám
        chapter_id = file_name.replace('.md', '').replace('/', '-')
        
        # Použiť poskytnuté číslo kapitoly
        self.section_counters = {'h1': 0, 'h2': 0, 'h3': 0}
        is_appendix = 'appendices' in file_name
        
        # Flag to track if this is the first header in the file
        is_first_header = [True]
        
        def add_header_numbering(match):
            level = int(match.group(1))
            text = match.group(2)
            # `text` comes from already-converted HTML, so smart quotes from the
            # 'smarty' extension are still literal entities (e.g. &lsquo;) at this
            # point. Unescape them before stripping punctuation, otherwise their
            # letters (lsquo/rsquo/amp/...) survive into the id and it no longer
            # matches the anchor extract_headers_for_toc computed from the raw
            # markdown text — breaking the TOC link and page-number lookup for
            # any heading containing a quote/apostrophe (e.g. "Halt!").
            header_id = re.sub(r'[^\w\s-]', '', html.unescape(text).lower())
            header_id = re.sub(r'[-\s]+', '-', header_id)
            
            # Generovať číslovanie
            # First header in each file should be treated as chapter title (H1 level numbering)
            if is_first_header[0]:
                is_first_header[0] = False
                self.section_counters['h2'] = 0
                self.section_counters['h3'] = 0
                if is_appendix:
                    number = f"A{chapter_num - self.num_root_files}."
                else:
                    number = f"{chapter_num}."
                # Force H1 styling for first header
                return f'<span class="page-marker" data-anchor="{chapter_id}-{header_id}"></span><h1 id="{chapter_id}-{header_id}" class="chapter-title"><span class="heading-number">{number}</span> {text}</h1>'
            elif level == 1:
                self.section_counters['h1'] += 1
                self.section_counters['h2'] = 0
                self.section_counters['h3'] = 0
                if is_appendix:
                    number = f"A{chapter_num - self.num_root_files}."
                else:
                    number = f"{chapter_num}."
            elif level == 2:
                self.section_counters['h2'] += 1
                self.section_counters['h3'] = 0
                if is_appendix:
                    number = f"A{chapter_num - self.num_root_files}.{self.section_counters['h2']}."
                else:
                    number = f"{chapter_num}.{self.section_counters['h2']}."
            elif level == 3:
                self.section_counters['h3'] += 1
                if is_appendix:
                    number = f"A{chapter_num - self.num_root_files}.{self.section_counters['h2']}.{self.section_counters['h3']}."
                else:
                    number = f"{chapter_num}.{self.section_counters['h2']}.{self.section_counters['h3']}."
            else:
                number = ""
            
            return f'<span class="page-marker" data-anchor="{chapter_id}-{header_id}"></span><h{level} id="{chapter_id}-{header_id}"><span class="heading-number">{number}</span> {text}</h{level}>'
        
        # Nahradiť všetky h1, h2, h3 s ID a číslovaním (vrátane tých s atribútmi)
        html_content = re.sub(r'<h([1-3])[^>]*>(.*?)</h\1>', add_header_numbering, html_content)

        html_content = self.colorize_cards(html_content)
        return html_content

    def colorize_cards(self, html: str) -> str:
        """Zafarbí YELLOW/RED/BLACK karty v tabuľkách trestov."""
        html = html.replace('<strong>YELLOW</strong>', '<strong class="card-yellow">YELLOW</strong>')
        html = html.replace('<strong>RED</strong>', '<strong class="card-red">RED</strong>')
        html = html.replace('<strong>BLACK</strong>', '<strong class="card-black">BLACK</strong>')
        return html

    def get_logo_base64(self) -> str:
        """Načíta logo a konvertuje na base64"""
        # Try JPG first, then PNG
        logo_jpg = Path('febus_logo.jpg')
        logo_png = Path('febus_logo.png')
        
        if logo_jpg.exists():
            with open(logo_jpg, 'rb') as f:
                logo_data = f.read()
                return 'data:image/jpeg;base64,' + base64.b64encode(logo_data).decode('utf-8')
        elif logo_png.exists():
            with open(logo_png, 'rb') as f:
                logo_data = f.read()
                return 'data:image/png;base64,' + base64.b64encode(logo_data).decode('utf-8')
        return ""
    
    def get_last_commit_date(self) -> str:
        """Získa dátum posledného commitu"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%cd', '--date=format:%d. %B %Y'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return datetime.datetime.now().strftime('%d. %B %Y')
    
    def get_commit_hash(self) -> str:
        """Získa hash posledného commitu"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def get_repository_url(self) -> str:
        """Získa URL git repozitára"""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True,
                check=True
            )
            url = result.stdout.strip()
            # Convert SSH to HTTPS format if needed
            if url.startswith('git@'):
                url = url.replace(':', '/').replace('git@', 'https://')
            if url.endswith('.git'):
                url = url[:-4]
            return url
        except:
            return "https://github.com/FEBUS/rulebook"

    def get_version(self) -> str:
        """Získa verziu rulebooku zo súboru VERSION"""
        p = Path('VERSION')
        return p.read_text(encoding='utf-8').strip() if p.exists() else ''

    def generate_changelog(self) -> str:
        """Vygeneruje changelog: preferuje CHANGELOG.md, fallback git história."""
        changelog_md = Path('CHANGELOG.md')
        if changelog_md.exists():
            md = markdown.Markdown(extensions=['extra', 'sane_lists'])
            body = md.convert(changelog_md.read_text(encoding='utf-8'))
            return f'<div class="changelog">{body}</div>'
        return self._generate_changelog_from_git()

    def _generate_changelog_from_git(self) -> str:
        """Vygeneruje changelog z git histórie (fallback, ak chýba CHANGELOG.md)"""
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%h | %ad | %s', '--date=short', '-20'],
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split('\n')
            
            changelog_html = '<div class="changelog">'
            changelog_html += '<h1>Change Log</h1>'
            changelog_html += '<p>Recent changes to the rulebook:</p>'
            changelog_html += '<table class="changelog-table">'
            changelog_html += '<thead><tr><th>Commit</th><th>Date</th><th>Description</th></tr></thead>'
            changelog_html += '<tbody>'
            
            for commit in commits[:10]:  # Posledných 10 commitov
                if commit:
                    parts = commit.split(' | ')
                    if len(parts) == 3:
                        commit_hash, date, message = parts
                        changelog_html += f'<tr><td class="commit-hash">{commit_hash}</td><td>{date}</td><td>{message}</td></tr>'
            
            changelog_html += '</tbody></table>'
            changelog_html += '</div>'
            
            return changelog_html
        except:
            return '<div class="changelog"><h1>Change Log</h1><p>No git history available.</p></div>'
    
    def extract_page_numbers_from_pdf(self, pdf_path: str) -> Dict[str, int]:
        """Extrahuje čísla strán pre kotvy z PDF cez named destinations.

        WeasyPrint vytvorí named destination pre každý `<a href="#anchor">`
        odkaz, ktorý má v dokumente zodpovedajúci `id`; TOC odkazuje na každú
        kotvu z self.toc_entries, takže za normálnych okolností sa každá
        kotva namapuje priamo na skutočnú stranu podľa PDF štruktúry, bez
        závislosti na texte nadpisu. Toto opravuje prípady, keď sa rovnaký
        text nadpisu (napr. "Arena boundaries", "Judging of hits") opakuje vo
        viacerých kapitolách/prílohách — staršie zhodovanie podľa titulku
        vracalo stranu prvého výskytu textu v CELOM dokumente (vrátane
        bežného textu, nie len nadpisov), nie skutočnú stranu danej kotvy.

        Predchádzajúca verzia mala pre nevyriešené kotvy záložné zhodovanie
        podľa titulku; to sa v praxi ukázalo nefunkčné (chybná posuvná
        oblasť hľadania a zhoda na hocijaký výskyt textu, nielen nadpis) a
        keďže named destinations pokrývajú všetky kotvy z TOC, bolo
        odstránené. Ak sa napriek tomu pre niektorú kotvu destination
        nenájde, hlasno sa to nahlási a číslo strany zostane v TOC prázdne
        (rovnaké degradované správanie, aké malo pôvodné zlyhanie extrakcie).
        """
        page_numbers = {}
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                named_destinations = {}
                try:
                    named_destinations = pdf_reader.named_destinations
                except Exception as e:
                    print(f"Varovanie: Nepodarilo sa načítať named destinations: {e}")

                unresolved = []
                for level, title, anchor in self.toc_entries:
                    dest = named_destinations.get(anchor)
                    if dest is None:
                        unresolved.append((title, anchor))
                        continue
                    try:
                        page_numbers[anchor] = pdf_reader.get_destination_page_number(dest) + 1
                    except Exception:
                        unresolved.append((title, anchor))

                if unresolved:
                    print(f"VAROVANIE: {len(unresolved)} položiek obsahu nemá named "
                          f"destination — ich číslo strany v TOC ostane prázdne: "
                          f"{[title for title, _ in unresolved]}")

        except Exception as e:
            print(f"Varovanie: Nepodarilo sa extrahovať čísla strán: {e}")

        return page_numbers

    def generate_pdf(self, output_filename: str = 'febus_rulebook.pdf'):
        """Vygeneruje PDF dokument"""
        print("Generujem PDF...")
        
        # Zbierať všetky HTML časti
        html_parts = []
        
        # Získať logo
        logo_data = self.get_logo_base64()
        logo_html = ""
        if logo_data:
            logo_html = f'<img src="{logo_data}" alt="FEBUS Logo" class="logo">'
        
        # Získať informácie o git
        last_commit_date = self.get_last_commit_date()
        commit_hash = self.get_commit_hash()
        repo_url = self.get_repository_url()
        version = self.get_version()
        edition = f'Official Edition — Version {version}' if version else 'Official Edition'

        # Titulná strana
        html_parts.append(f'''
            <div class="title-page">
                <div class="title-top">
                    <div class="logo-container">
                        {logo_html}
                    </div>
                </div>
                <div class="title-middle">
                    <div class="main-title">
                        <span class="title-line1">Tournament</span>
                        <span class="title-line2">Rulebook</span>
                    </div>
                    <div class="subtitle">FEBUS</div>
                    <div class="divider">❦</div>
                </div>
                <div class="title-bottom">
                    <div class="edition">{edition}</div>
                    <div class="version-date">{last_commit_date}</div>
                    <div class="publisher">Federácia Európskych Bojových Umení Slovenska</div>
                </div>
                <div class="colophon">
                    <span class="repo-link">{repo_url}</span>
                </div>
            </div>
        ''')
        
        # Spracovať každý markdown súbor
        chapter_num = 0
        for file_name, file_path in self.md_files:
            print(f"Spracovávam: {file_name}")
            chapter_num += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extrahovať hlavičky pre obsah s číslovaním
            self.extract_headers_for_toc(content, file_name, chapter_num)
            
            # Konvertovať na HTML s číslom kapitoly
            html_content = self.convert_markdown_to_html(content, file_name, chapter_num)
            
            # Pridať do výsledku
            chapter_id = file_name.replace('.md', '').replace('/', '-')
            html_parts.append(f'<div class="chapter" id="{chapter_id}">')
            html_parts.append(html_content)
            html_parts.append('</div>')
            html_parts.append('<div class="page-break"></div>')
        
        # Pridať changelog na koniec
        changelog_html = self.generate_changelog()
        html_parts.append(changelog_html)
        
        # Vygenerovať obsah (najprv bez čísel strán)
        toc_html = self.generate_table_of_contents(with_page_numbers=False)
        
        # CSS štýly
        css_styles = '''
            @page {
                size: A4;
                margin: 3cm 2.5cm 3cm 2.5cm;
                
                @top-center {
                    content: "FEBUS TOURNAMENT RULEBOOK";
                    font-family: 'Times New Roman', Times, serif;
                    font-size: 9pt;
                    color: #999;
                    font-variant: small-caps;
                    letter-spacing: 0.05em;
                }
                
                @bottom-center {
                    content: counter(page);
                    font-family: 'Times New Roman', Times, serif;
                    font-size: 10pt;
                }
            }
            
            @page:first {
                @top-center { content: ""; }
                @bottom-center { content: ""; }
                @bottom-right { content: ""; }
            }
            
            body {
                font-family: 'Times New Roman', Times, serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #111;
                text-align: justify;
                hyphens: auto;
                word-spacing: 0.05em;
                letter-spacing: 0.01em;
            }
            
            /* Nadpisy - Book Style */
            h1 {
                font-size: 20pt;
                font-weight: normal;
                margin: 2em 0 1em 0;
                page-break-after: avoid;
                page-break-inside: avoid;
                color: #000;
                text-align: center;
                border: none;
                font-variant: small-caps;
                letter-spacing: 0.1em;
            }
            
            h2 {
                font-size: 16pt;
                font-weight: bold;
                margin: 1.2em 0 0.6em 0;
                page-break-after: avoid;
                page-break-inside: avoid;
                color: #111;
                text-align: left;
            }
            
            h3 {
                font-size: 13pt;
                font-weight: bold;
                margin: 1em 0 0.5em 0;
                page-break-after: avoid;
                page-break-inside: avoid;
                color: #222;
                text-align: left;
                font-style: italic;
            }
            
            h4 {
                font-size: 11pt;
                font-weight: bold;
                font-style: italic;
                margin: 0.8em 0 0.4em 0;
                page-break-after: avoid;
                page-break-inside: avoid;
                color: #333;
            }
            
            /* Číslovanie nadpisov */
            .heading-number {
                font-weight: bold;
                margin-right: 0.5em;
                color: #000;
            }
            
            /* Odstavce */
            p {
                margin: 0 0 0.8em 0;
                text-indent: 0;
                orphans: 3;
                widows: 3;
                text-align: justify;
                hyphens: none;
            }
            
            /* Prvý odstavec po nadpise */
            h1 + p, h2 + p, h3 + p, h4 + p,
            .chapter > p:first-of-type {
                text-indent: 0;
                margin-top: 0.5em;
            }
            
            /* Zoznamy */
            ul, ol {
                margin: 0.8em 0 0.8em 1.5em;
                padding-left: 0.5em;
            }
            
            li {
                margin-bottom: 0.3em;
                text-align: justify;
            }
            
            li p {
                margin-bottom: 0.3em;
                display: inline;
            }
            
            /* Tables - Book Style */
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 2em 0;
                page-break-inside: auto;
                font-size: 10pt;
            }
            
            tr {
                page-break-inside: avoid;
                break-inside: avoid;
            }

            th, td {
                border: none;
                border-top: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                padding: 0.5em 1em;
                text-align: left;
            }
            
            th {
                background: none;
                font-weight: bold;
                font-variant: small-caps;
                letter-spacing: 0.05em;
                border-top: 2px solid #333;
                border-bottom: 1px solid #333;
            }
            
            tbody tr:last-child td {
                border-bottom: 2px solid #333;
            }

            .card-yellow { background-color: #E3D059; padding: 0 4px; white-space: nowrap; }
            .card-red    { background-color: #E36159; color: #fff; padding: 0 4px; white-space: nowrap; }
            .card-black  { background-color: #787878; color: #fff; padding: 0 4px; white-space: nowrap; }

            /* Citácie */
            blockquote {
                margin: 1em 2em;
                padding-left: 1em;
                border-left: 3px solid #999;
                font-style: italic;
                color: #555;
            }
            
            /* Kód */
            code {
                font-family: 'Courier New', Courier, monospace;
                font-size: 10pt;
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 2px;
            }
            
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 10pt;
                line-height: 1.4;
            }
            
            /* Stránkovanie */
            .page-break {
                page-break-after: always;
            }
            
            .chapter {
                page-break-before: always;
            }
            
            .chapter:first-of-type {
                page-break-before: avoid;
            }
            
            /* Professional Book Title Page */
            .title-page {
                page-break-after: always;
                position: relative;
                height: 100vh;
                display: flex;
                flex-direction: column;
                font-family: 'Times New Roman', Times, serif;
                text-align: center;
            }
            
            /* Top section with logo */
            .title-top {
                flex: 0 0 auto;
                padding-top: 3cm;
            }
            
            .logo-container {
                margin: 0 auto;
            }
            
            .title-page .logo {
                width: 180px;
                height: auto;
                margin: 0 auto;
                display: block;
            }
            
            /* Middle section with title */
            .title-middle {
                flex: 1 1 auto;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 2cm 0;
            }
            
            .main-title {
                margin-bottom: 0.8em;
                color: #000;
                font-variant: small-caps;
                line-height: 0.9;
            }
            
            .title-line1, .title-line2 {
                display: block;
                font-weight: normal;
            }
            
            .title-line1 {
                font-size: 48pt;
                letter-spacing: 0.12em;
            }
            
            .title-line2 {
                font-size: 48pt;
                letter-spacing: 0.08em;
            }
            
            .subtitle {
                font-size: 28pt;
                font-weight: normal;
                letter-spacing: 0.15em;
                margin-bottom: 1em;
                color: #333;
                font-variant: small-caps;
            }
            
            .divider {
                font-size: 18pt;
                color: #666;
                margin: 1em 0;
            }
            
            /* Bottom section with publication info */
            .title-bottom {
                flex: 0 0 auto;
                padding-bottom: 3cm;
            }
            
            .edition {
                font-size: 12pt;
                font-variant: small-caps;
                letter-spacing: 0.1em;
                margin-bottom: 0.5em;
                color: #555;
            }
            
            .version-date {
                font-size: 11pt;
                margin-bottom: 1em;
                color: #666;
            }
            
            .publisher {
                font-size: 10pt;
                font-style: italic;
                color: #777;
                margin-bottom: 2em;
            }
            
            /* Colophon at very bottom */
            .colophon {
                position: absolute;
                bottom: 1cm;
                left: 0;
                right: 0;
                text-align: center;
            }
            
            .repo-link {
                font-size: 7pt;
                color: #ccc;
                font-family: 'Courier New', Courier, monospace;
            }
            
            /* Clean Table of Contents */
            .toc {
                page-break-after: always;
                font-family: 'Times New Roman', Times, serif;
            }
            
            .toc-title {
                font-size: 18pt;
                font-weight: bold;
                text-align: center;
                margin: 1.5em 0 2em 0;
                letter-spacing: 0.1em;
                border: none;
            }
            
            .toc-content {
                margin: 0 3em;
                line-height: 1.8;
            }
            
            .toc-line {
                display: flex;
                align-items: baseline;
                width: 100%;
                position: relative;
                page-break-inside: avoid;
            }
            
            .toc-text {
                flex: 0 0 auto;
                padding-right: 0.3em;
            }
            
            .toc-text a {
                text-decoration: none;
                color: #000;
            }
            
            .toc-text a:hover {
                text-decoration: underline;
            }
            
            .toc-dots {
                flex: 1 1 auto;
                border-bottom: 1px dotted #666;
                margin: 0 0.5em;
                height: 0.7em;
            }
            
            .toc-page {
                flex: 0 0 auto;
                min-width: 3em;
                text-align: right;
            }
            
            /* Level 1 - Main chapters */
            .toc-level-1 {
                margin: 0.8em 0 0.4em 0;
                font-weight: bold;
                font-size: 11pt;
            }
            
            .toc-level-1 .toc-text {
                text-transform: uppercase;
            }
            
            /* Level 2 - Sections */
            .toc-level-2 {
                margin: 0.3em 0 0.2em 2em;
                font-size: 10pt;
                font-weight: normal;
            }
            
            /* Level 3 - Subsections - hide from TOC */
            .toc-level-3 {
                display: none;
            }
            
            /* Page marker for finding positions */
            .page-marker {
                display: block;
                height: 0;
                width: 0;
                overflow: hidden;
                page-break-after: avoid;
            }
            
            /* Changelog */
            .changelog {
                page-break-before: always;
                margin-top: 2em;
            }
            
            .changelog h1 {
                font-size: 24pt;
                border-bottom: 2px solid #000;
                padding-bottom: 0.3em;
            }
            
            .changelog-table {
                width: 100%;
                margin-top: 1em;
                border-collapse: collapse;
                font-size: 10pt;
            }
            
            .changelog-table th,
            .changelog-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            
            .changelog-table th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
            
            .commit-hash {
                font-family: 'Courier New', Courier, monospace;
                font-size: 9pt;
                color: #666;
            }
        '''
        
        # Vytvoriť kompletný HTML dokument
        html_document = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>FEBUS Tournament Rulebook</title>
            <style>{css_styles}</style>
        </head>
        <body>
            {html_parts[0]}
            {toc_html}
            {''.join(html_parts[1:])}
        </body>
        </html>
        '''
        
        # Vygenerovať dočasné PDF pre získanie čísel strán
        font_config = FontConfiguration()
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
            html = HTML(string=html_document)
            html.write_pdf(temp_pdf_path, font_config=font_config)
        
        # Extrahovať čísla strán
        print("Extraktujem čísla strán...")
        self.page_numbers = self.extract_page_numbers_from_pdf(temp_pdf_path)
        
        if self.page_numbers:
            # Znovu vygenerovať obsah s číslami strán
            print("Aktualizácia obsahu s číslami strán...")
            toc_html = self.generate_table_of_contents(with_page_numbers=True)
            
            # Znovu vytvor HTML dokument s aktualizýam obsahom
            html_document = f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>FEBUS Tournament Rulebook</title>
                <style>{css_styles}</style>
            </head>
            <body>
                {html_parts[0]}
                {toc_html}
                {''.join(html_parts[1:])}
            </body>
            </html>
            '''
            
            # Vygenerovať finálne PDF
            html = HTML(string=html_document)
            html.write_pdf(output_filename, font_config=font_config)
        else:
            # Ak sa nepodarilo získať čísla strán, použiť dočasné PDF
            import shutil
            shutil.move(temp_pdf_path, output_filename)
        
        # Vymazať dočasný súbor
        try:
            os.unlink(temp_pdf_path)
        except:
            pass
        
        print(f"PDF vygenerované: {output_filename}")

def main():
    """Hlavná funkcia"""
    print("FEBUS Rulebook - Markdown to PDF Converter")
    print("=" * 50)
    
    converter = MarkdownToPDFConverter()
    
    # Zozbierať súbory
    files = converter.collect_markdown_files()
    print(f"Nájdených {len(files)} markdown súborov")
    
    # Vygenerovať PDF
    output_file = 'febus_rulebook.pdf'
    converter.generate_pdf(output_file)
    
    print("=" * 50)
    print(f"Hotovo! PDF dokument bol vytvorený: {output_file}")

if __name__ == "__main__":
    main()