class FeedError(Exception):
    pass


class FeedParsingError(FeedError):
    pass


class FeedDownloadError(FeedError):
    pass


class FeedValidationError(FeedError):
    pass
