#! /bin/bash

# If $DEBIAN_PREFIX is set, it will be prepended to all locations.
# This is used when building the Debian package.

set -e

##

if ! kde4-config 2>/dev/null; then
    echo >&2 "ERROR: could not find kde4-config."
    exit 1
fi

##

PREFIX=`kde4-config --prefix`
BIN=`kde4-config --install exe`
APPS=`kde4-config --install data`
ICONS=`kde4-config --install icon`
DESKTOP=`kde4-config --install xdgdata-apps`
SERVICE_MENUS=`kde4-config --install services`/ServiceMenus
MINIROK="$APPS/minirok"

##

install_file () {
    # path/file path/dir -> path/dir/file
    install_file2 "$1" "$2/`basename $1`"
}

install_file2 () {
    # path/file path/dir/file2 -> path/dir/file2
    install -D -m `mode $1` "$1" "${DEBIAN_PREFIX%%/}/${2##/}"
}

install_symlink () {
    DEST="${DEBIAN_PREFIX%%/}/${2##/}"
    mkdir -p "`dirname $DEST`"
    ln -sf "$1" "$DEST"
}

##

install_icons () {
    ( cd "$1" && find -maxdepth 1 -name '*.png' ) | while read file; do
    	install_file2 "$1/$file" "$2/`echo $file | tr = /`"
    done
}

install_images () {
    for img in images/*.png; do
    	install_file "$img" "$MINIROK/images"
    done
}

install_package () {
    for p in minirok.py minirok/*.py minirok/ui/*.py; do
    	install_file "$p" "$PREFIX/share/minirok/`dirname $p`"
    done
}

install_manpage () {
    if make -s minirok.1; then
    	install_file minirok.1 /usr/share/man/man1
    fi
}

##

mode () {
    if [ -x "$1" ]; then
    	echo 755
    else
    	echo 644
    fi
}

##

case "$1" in
    install)
	install_images
	install_package
	install_manpage
	install_icons images/icons "$ICONS"
	install_icons images/icons/private "$MINIROK/icons"
	install_file config/minirokui.rc "$MINIROK"
	install_file config/minirok.desktop "$DESKTOP"
	install_file config/minirok_append.desktop "$SERVICE_MENUS"
	install_symlink "$PREFIX/share/minirok/minirok.py" "$BIN/minirok"
	;;

    *)
	echo "Doing nothing, please pass 'install' as the first argument."
	;;
esac
