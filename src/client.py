"""
Defines the news reader class ``NewsReader`` which allows fetching news based
on various endpoints and various parameters supported by https://newsapi.org/.

:author: Gaurav
:date: 20190702
"""

import logging
import requests
import sys

logger = logging.getLogger("client.NewsReader")

ALL = 'ALL'

ALLOWED_COUNTRY = {
    'ae', 'ar', 'at', 'au', 'be', 'bg', 'br', 'ca', 'ch', 'cn', 'co', 'cu',
    'cz', 'de', 'eg', 'fr', 'gb', 'gr', 'hk', 'hu', 'id', 'ie', 'il', 'in',
    'it', 'jp', 'kr', 'lt', 'lv', 'ma', 'mx', 'my', 'ng', 'nl', 'no', 'nz',
    'ph', 'pl', 'pt', 'ro', 'rs', 'ru', 'sa', 'se', 'sg', 'si', 'sk', 'th',
    'tr', 'tw', 'ua', 'us', 've', 'za'
}

ALLOWED_CATEGORY = {
    'business', 'entertainment', 'general', 'healt','science', 'sports'
    'technology'
}

ALLOWED_LANGUAGE = {
    'ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'se',
    'ud', 'zh'
}

class NewsReader:

    def __init__(self, apikey):
        """
        Register your NewsReader with the `apikey` APIKEY. For more
        information on how to get the apikey, please refer to
        https://newsapi.org/.
        """
        self.apikey = apikey
        self.url    = 'https://newsapi.org/v2'

    def get_headlines(self, country=ALL, category=ALL, sources=ALL, q=None,
                      pageSize=20, pageNo=1):
        assert country == ALL or country in ALLOWED_COUNTRY, \
            "Country should be one of '{}'".format(ALLOWED_COUNTRY)
        assert category == ALL or category in ALLOWED_CATEGORY, \
            "Category should be one of '{}'".format(ALLOWED_CATEGORY)
        pass

    def _get_sources(self, category=ALL, language=ALL, country=ALL):
        """
        Returns information about sources (supported by https://newsapi.org).

        :param category: category of news, can be one of `ALLOWED_CATEGORY`.
        :type category: ``str``

        :param language: language of news, can be one of `ALLOWED_LANGUAGE`.
        :type language: ``str``

        :param country: Country id, can be one of `ALLOWED_COUNTRY`.
        :type country: ``str``

        :return: ``list`` of ``dict`` containing information about channel
          sources.
        """
        assert category ==  ALL or category in ALLOWED_CATEGORY, \
            "Category should be one of '{}'".format(ALLOWED_CATEGORY)
        assert language == ALL or language in ALLOWED_LANGUAGE, \
            "language should be one of '{}'".format(ALLOWED_LANGUAGE)
        assert country == ALL or country in ALLOWED_COUNTRY, \
            "Country should be one of '{}'".format(ALLOWED_COUNTRY)
        sources = self._request(endpoint='sources', category=category,
                                language=language, country=country)
        sources = sources['sources']
        return sources

    def _get_sources_info(self, infotype, category=ALL, language=ALL,
                          country=ALL):
        """
        Returns particular information about the sources (specified as
        `infotype`).

        :param infotype: Type of information to be fetched from sources, can be
          one or more of `id`, `name`, `description`, `url`, `category`,
          `language` or `country`.

        :param category: category of news, can be one of `ALLOWED_CATEGORY`.
        :type category: ``str``

        :param language: language of news, can be one of `ALLOWED_LANGUAGE`.
        :type language: ``str``

        :param country: Country id, can be one of `ALLOWED_COUNTRY`.
        :type country: ``str``
        """
        sources = self._get_sources(category=category, language=language,
                                    country=country)
        slist = list()
        if isinstance(infotype, (list, tuple)):
            # User asked to fetch more than 1 type of information
            # In such a case, return list of `dict`.
            for s in sources:
                info = {}
                for i in infotype:
                    info[i] = s[i]
                slist.append(info)
        else:
            for s in sources:
                slist.append(s[infotype])
        return slist

    def _url_join(self, prefix, *parts, query_string=""):
        """
        Joins various parts of the url to form a complete/correct URL.
        
        :param prefix:
            The prefix/domain part of the URL. For e.g., https://foo.bar/.
        :type prefix:
            ``str``

        :param parts:
            Various parts that make a valid endpoint. For example:
            /foo/bar/def in some domain should be given as "foo", "bar" and
            "def".
        :type parts:
            ``str``

        :param query_string:
            `GET` parameters to be appended to the query.
        """
        if not prefix.endswith("/"):
            prefix += "/"
        all_parts = ""
        for part in parts:
            if part.startswith("/"):
                part = part[1:]
            all_parts += part
        if query_string != "":
            if not query_string.startswith("?"):
                query_string = "?" + query_string
            all_parts += query_string
        return prefix + all_parts

    def _add_apikey_param(self, query_string=''):
        """
        Adds APIKEY to the `query_string` param.
        """
        if query_string is '':
            return "apikey={}".format(self.apikey)
        return query_string + "&apikey={}".format(self.apikey)

    def _request(self, endpoint, **kwargs):
        """
        Central utility to send request to `endpoint` with `GET` parameters
        from `kwargs` passed.

        :return: ``json`` response from the request sent to the `endpoint`
        """
        params = []
        default_values = (ALL, '', None)
        for arg, value in kwargs.items():
            if value in default_values:
                continue
            params.append('{}={}'.format(arg, value))
        get_params = "&".join(params)
        get_params = self._add_apikey_param(get_params)
        url = self._url_join(self.url, endpoint, query_string=get_params)

        # Send a GET request to the url
        req = requests.get(url)
        resp = req.json()
        if req.status_code == 200:
            logger.info("[INFO] Request to '{}' was successful!".format(url))
            return resp
        logger.error("[ERROR] Status code: {}".format(req.status_code))
        logger.error(
            "[ERROR] '{}': '{}'".format(resp['code'], resp['message'])
        )
        sys.exit(1)
