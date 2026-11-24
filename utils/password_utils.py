import getpass
import sys


def leer_clave(prompt="Contraseña: "):
    """Lee una contraseña mostrando un asterisco por cada carácter.

    Si la consola no es un terminal real (por ejemplo, la consola de Run
    de PyCharm sin 'Emulate terminal'), usa getpass como alternativa.
    """
    if not sys.stdin.isatty():
        return getpass.getpass(prompt)

    sys.stdout.write(prompt)
    sys.stdout.flush()
    caracteres = []

    try:
        import msvcrt  # Windows

        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                break
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch in ("\b", "\x7f"):
                if caracteres:
                    caracteres.pop()
                    sys.stdout.write("\b \b")
            elif ch in ("\x00", "\xe0"):
                msvcrt.getwch()  # tecla especial (flechas, etc.): se ignora
            else:
                caracteres.append(ch)
                sys.stdout.write("*")
            sys.stdout.flush()

    except ImportError:
        import termios
        import tty  # Linux / macOS

        fd = sys.stdin.fileno()
        antiguo = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    sys.stdout.write("\r\n")
                    break
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch in ("\b", "\x7f"):
                    if caracteres:
                        caracteres.pop()
                        sys.stdout.write("\b \b")
                else:
                    caracteres.append(ch)
                    sys.stdout.write("*")
                sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, antiguo)

    return "".join(caracteres)