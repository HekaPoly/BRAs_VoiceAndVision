import record
import faulthandler
faulthandler.enable()


def main():
    text = record.transcribe_directly()
    print(text)

if __name__ == '__main__':
    main()
    