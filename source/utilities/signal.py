import signal

def on_sigterm():
    bot.quit()
    sys.exit(0)

signal.signal(signal.SIGTERM, on_sigterm)