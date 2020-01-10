#!/usr/bin/env python
#
from __future__ import absolute_import

import json

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["OnePasswordURLProvider"]

# Variables for the update URL:
# - https://app-updates.agilebits.com/check/1/
# - Kernel version
# - String "OPM4"
# - Locale
# - The 1Password build number to update from
UPDATE_URLS = {
    "4": "https://app-updates.agilebits.com/check/1/13.0.0/OPM4/en/400600",
    "5": "https://app-updates.agilebits.com/check/1/14.0.0/OPM4/en/500000",
    "6": "https://app-updates.agilebits.com/check/1/14.0.0/OPM4/en/553001",
    "7": "https://app-updates.agilebits.com/check/1/18.0.0/OPM7/en/700000",
}

DEFAULT_SOURCE = "Amazon CloudFront"
DEFAULT_MAJOR_VERSION = "6"


class OnePasswordURLProvider(URLGetter):
    """Provides a download URL for the latest 1Password"""

    input_variables = {
        "major_version": {
            "required": False,
            "description": (
                "The 1Password major version to get. "
                "Possible values are '4', '5', '6', or '7' and the default "
                "is '%s'" % DEFAULT_MAJOR_VERSION
            ),
        },
        "base_url": {
            "required": False,
            "description": "The 1Password update check URL",
        },
        "source": {
            "required": False,
            "description": (
                "Where to download the disk image. "
                "Possible values are 'Amazon CloudFront', 'CacheFly' and 'AgileBits'. "
                "Default is %s." % DEFAULT_SOURCE
            ),
        },
    }
    output_variables = {
        "url": {"description": "URL to the latest 1Password release.",},
    }
    description = __doc__

    def get_1Password_dmg_url(self, base_url, preferred_source):
        """Find and return a download URL"""

        self.output("Preferred source is %s" % preferred_source)

        # 1Password update check gets a JSON response from the server.
        # Grab it and parse...
        update_data = json.loads(self.download(base_url))
        version = update_data.get("version", None)
        self.output("Found version %s" % version)

        sources = update_data.get("sources", [])
        found_source = next(
            (src for src in sources if src["name"] == preferred_source), None
        )
        if not found_source:
            raise ProcessorError("No download source for %s" % preferred_source)

        source_url = found_source.get("url", None)
        if not source_url:
            raise ProcessorError("No URL found for %s" % preferred_source)

        return source_url

    def main(self):
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)
        if major_version not in UPDATE_URLS:
            raise ProcessorError(
                "Unsupported value for major version: %s" % major_version
            )

        update_url = UPDATE_URLS[major_version]
        base_url = self.env.get("base_url", update_url)
        source = self.env.get("source", DEFAULT_SOURCE)
        self.env["url"] = self.get_1Password_dmg_url(base_url, source)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = OnePasswordURLProvider()
    processor.execute_shell()
