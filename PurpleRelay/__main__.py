import CoreService
import warnings
import bs4


def main():
    warnings.filterwarnings(action='ignore', category=bs4.MarkupResemblesLocatorWarning,
                            message='[\s\S]+ looks like a URL. Beautiful Soup is not an HTTP client.[\s\S]+')
    CoreService.CoreService.run()


if __name__ == "__main__":
    main()
