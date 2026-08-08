#!/bin/bash
# Konvenčné kontroly rulebooku. Exit 0 = OK. Kontroluje kapitoly a appendices,
# nie docs/ ani slovenské súbory.
set -u
FILES="01-intro.md 02-equipment.md 03-general.md 04-right-of-way.md \
05-longsword.md 06-rapier.md 07-sabre.md 08-sword-and-buckler.md \
09-organisational.md 10-disciplinary.md README.md appendices/01-glossary.md \
appendices/02-penalties.md"
fail=0
check_zero() {  # $1 = popis, $2 = pattern
  hits=$(grep -nE "$2" $FILES 2>/dev/null)
  if [ -n "$hits" ]; then echo "FAIL: $1"; echo "$hits"; fail=1; fi
}
check_zero "zakázané modálne tvary"        '\bshall\b|is going to'
check_zero "nekanonické osoby"              '\bcontestants?\b|\bcompetitors?\b|\bathletes?\b'
check_zero "nekanonický súboj"              '\bthe match\b|\bthe fight\b'
check_zero "rodové zámená"                  'he/she|she/he|his/her|him/her|him/them'
check_zero "nekanonická priorita"           'right of initiative'
check_zero "nekanonická čiara"              'start-line|\bstarting line\b'
check_zero "nekanonický asistent"           'Side Referee'
check_zero "americký pravopis organizácie"  'Organizing Team|organizer'
check_zero "nekanonický cross-guard"        '\bcrossguard\b|cross/guard'
check_zero "nekanonický stop hit"           '\bstop hit\b'
check_zero "rozbité FIE odkazy"             'Article [0-9]|in Article\.|Figure 2'
check_zero "staré HTML atribúty"            'bgcolor'
exit $fail
