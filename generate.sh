#!/bin/bash

# FEBUS Rulebook PDF Generator
# Automatický skript pre generovanie PDF dokumentu z Markdown súborov

set -e  # Zastaviť pri chybe

# Farby pre výpis
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Banner
echo "=================================================="
echo "    FEBUS Rulebook - PDF Generator"
echo "=================================================="
echo ""

# Kontrola Python3
echo -e "${YELLOW}🔍 Kontrolujem Python3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 nie je nainštalovaný!${NC}"
    echo "Prosím nainštalujte Python3: brew install python3"
    exit 1
fi
echo -e "${GREEN}✓ Python3 nájdený${NC}"

# Kontrola a vytvorenie virtuálneho prostredia
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Vytváram virtuálne prostredie...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtuálne prostredie vytvorené${NC}"
else
    echo -e "${GREEN}✓ Virtuálne prostredie existuje${NC}"
fi

# Aktivácia virtuálneho prostredia
echo -e "${YELLOW}🚀 Aktivujem virtuálne prostredie...${NC}"
source venv/bin/activate

# Kontrola a inštalácia závislostí
echo -e "${YELLOW}📚 Kontrolujem závislosti...${NC}"
if ! pip show markdown &> /dev/null || ! pip show weasyprint &> /dev/null; then
    echo -e "${YELLOW}📥 Inštalujem závislosti...${NC}"
    pip install --quiet -r requirements.txt
    echo -e "${GREEN}✓ Závislosti nainštalované${NC}"
else
    echo -e "${GREEN}✓ Závislosti sú už nainštalované${NC}"
fi

# Spustenie generovania PDF
echo ""
echo -e "${YELLOW}📄 Generujem PDF dokument...${NC}"
echo "=================================================="

python generate_pdf.py

# Kontrola výsledku
if [ -f "febus_rulebook.pdf" ]; then
    echo ""
    echo -e "${GREEN}✅ PDF dokument bol úspešne vygenerovaný!${NC}"
    
    # Zobrazenie informácií o súbore
    FILE_SIZE=$(ls -lh febus_rulebook.pdf | awk '{print $5}')
    echo -e "${GREEN}📊 Veľkosť súboru: ${FILE_SIZE}${NC}"
    
    # Ponuka na otvorenie
    echo ""
    echo -e "${YELLOW}Chcete otvoriť PDF dokument? (a/n)${NC}"
    read -n 1 -r
    echo
    if [[ $REPLY =~ ^[Aa]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open febus_rulebook.pdf
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open febus_rulebook.pdf 2>/dev/null || echo "Prosím otvorte súbor manuálne: febus_rulebook.pdf"
        else
            echo "PDF dokument: febus_rulebook.pdf"
        fi
    fi
else
    echo -e "${RED}❌ Chyba pri generovaní PDF!${NC}"
    exit 1
fi

# Deaktivácia virtuálneho prostredia
deactivate

echo ""
echo "=================================================="
echo -e "${GREEN}✨ Hotovo!${NC}"
echo "=================================================="