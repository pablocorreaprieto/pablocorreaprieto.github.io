#!/usr/bin/env bash
# Embeds creator, credit, copyright and CC BY 4.0 licence metadata in a figure or cover.
# Only for figures and covers Pablo made or confirmed as his, never for photos of him.
#
#   tools/tag-image.sh <image> <year> <fr|en|es> "<description = the image's alt text>"
#
# Needs exiftool (Debian/Ubuntu: apt-get install -y libimage-exiftool-perl).
set -euo pipefail
[ $# -eq 4 ] || { echo "usage: $0 <image> <year> <fr|en|es> <description>" >&2; exit 1; }
img=$1 year=$2 lang=$3 desc=$4
case $lang in
  fr) reuse=https://pablocorreaprieto.ch/reutilisation-figures ;;
  en) reuse=https://pablocorreaprieto.ch/en/figure-reuse ;;
  es) reuse=https://pablocorreaprieto.ch/es/reutilizacion-figuras ;;
  *) echo "lang must be fr, en or es" >&2; exit 1 ;;
esac
name="Pablo Correa Prieto"
notice="© $year $name — CC BY 4.0"
cc=https://creativecommons.org/licenses/by/4.0/
exiftool -q -overwrite_original -charset iptc=UTF8 -codedcharacterset=utf8 \
  "-XMP-dc:Creator=$name" "-EXIF:Artist=$name" "-IPTC:By-line=$name" \
  "-XMP-photoshop:Credit=$name" "-IPTC:Credit=$name" \
  "-XMP-dc:Rights=$notice" "-EXIF:Copyright=$notice" "-IPTC:CopyrightNotice=$notice" \
  "-XMP-xmpRights:WebStatement=$cc" "-XMP-xmpRights:Marked=True" \
  "-XMP-cc:License=$cc" "-XMP-cc:AttributionName=$name" "-XMP-plus:LicensorURL=$reuse" \
  "-XMP-dc:Description=$desc" "-EXIF:ImageDescription=$desc" "-IPTC:Caption-Abstract=$desc" \
  "$img"
echo "tagged $img"
