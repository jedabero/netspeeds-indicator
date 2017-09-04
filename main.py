import signal
import gi
import time
from os.path import dirname, abspath
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject

APP_ID = 'com.jedabero.netspeeds-indicator'
INTERVAL = 2  # seconds


def get_bytes(source, interface='enp2s0'):
    file = '/sys/class/net/' + interface + '/statistics/' + source + '_bytes'
    with open(file, 'r') as f:
        data = f.read()
    return int(data)


def bytes_to_readable(bytes):
    if bytes > 1024*1024:
        return "{0:.2f}".format(bytes / (1024*1024)) + " MB"
    elif bytes > 1024:
        return "{0:.2f}".format(bytes / 1024) + " KB"
    else:
        return str(bytes) + " B"


def check(indicator):
    tx_prev = 0
    rx_prev = 0
    while True:
        time.sleep(INTERVAL)
        tx = get_bytes('tx')
        rx = get_bytes('rx')
        tx_speed = tx - tx_prev
        rx_speed = rx - rx_prev
        test = bytes_to_readable(tx_speed) + "ps, " + bytes_to_readable(rx_speed) + "ps"
        GObject.idle_add(indicator.set_label, test, APP_ID, priority=GObject.PRIORITY_DEFAULT)
        tx_prev = tx
        rx_prev = rx


def app_quit(_):
    Gtk.main_quit()


def main():
    icon_path = dirname(abspath(__file__)) + '/icon.svg'
    indicator = AppIndicator3.Indicator.new(APP_ID, icon_path, AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    menu = Gtk.Menu()
    item_quit = Gtk.MenuItem('Salir')
    item_quit.connect('activate', app_quit)
    menu.append(item_quit)
    indicator.set_menu(menu)
    menu.show_all()

    update = Thread(target=check, args=(indicator,))
    update.setDaemon(True)
    update.start()

    Gtk.main()


if __name__ == "__main__":
    GObject.threads_init()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
