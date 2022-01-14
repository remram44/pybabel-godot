#!/bin/sh
set -eu

(cd testproject/ && pybabel extract -F babelrc -k Label/text -k Resource/catchphrase -k Node2D/catchphrase -k tr -o translations_new.pot .)

sed -e '/POT-Creation-Date/d' -e 's/\b20[0-9][0-9]\b/2020/' -e 's/Babel [0-9.]\+/Babel 2.0/' <testproject/translations.pot >expected.pot
sed -e '/POT-Creation-Date/d' -e 's/\b20[0-9][0-9]\b/2020/' -e 's/Babel [0-9.]\+/Babel 2.0/' <testproject/translations_new.pot >actual.pot
diff -u expected.pot actual.pot
