# coding: utf-8
# Author: João S. O. Bueno

import ast
import csv
from cStringIO import StringIO

import soundcloud
from requests.exceptions import HTTPError
#requests si not listed on the package requirements, but it is
# pre-requisite of the "soundcloud"


from sc.transmogrifier.utils import blueprint
from sc.transmogrifier.utils import BluePrintBoiler
from sc.transmogrifier.utils import NothingToDoHere

from sc.blueprints.soundcloud import logger


"""
Blueprint section for uploading audio files to
soundcloud infrastructure.


The "item" should have a "file" key, with a
"data" section - withthe file data -
optional sound file metada should be keys on item["file"]
"""


# attention to the "{track_id}" bit
SOUNDCLOUD_TEMPLATE_URL = ("http://w.soundcloud.com/player/?"
    "url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"
    "{track_id}&amp;show_artwork=true"

@blueprint("sc.blueprints.soundcloud.upload")
class Upload(BluePrintBoiler):
    def set_options(self):
        try:
            self.token = self.options[access_token]
        except KeyError:
            # FIXME: allow other ways of fetching the access token.
            # TODO: create a Plone view to allow one to get a proper
            # tokeb=n, to go with the product.
            logger.error("The sc.blueprints.soundcloud.upload blueprint"
                         " needs a valid soundcloud access token with"
                         " upload rights to be able to proceed. For now,"
                         " token should be passed as an \"acces_token\" "
                         "option on the cfg file. "
                         "This blueprint is **DISABLED** for this run")
            return
        try:
            self.client = soundcloud.Client(access_token = self.token)
        except HTTPError:
            logger.error("Could not retrieve a valid client to the"
                         " soundcloud API. Most likely the acces_token"
                         " in the configuration is invalid or expired."
                         "Please check the docs on how to get a new token"
                         "This blueprint is **DISABLED** for this run")
        # Wether to remove the sound datafrom the item before dispacthing
        # it through the pipeline

        self.remove_data = ast.literal_eval(self.options.get(
            "remove_data", "True"))
        self.audio_types = ast.literal_eval(self.options.get(
            "audio_types", """{"sound", "sc.embedder"}"""))
        self.url_template = self.options.get(
            "url_template", SOUNDCLOUD_TEMPLATE_URL)

        self.default_track_name = self.options.get("default_track_name", "Plone audio file")



    def transmogrify(self, item):
        if self.remove_data:
            data = item.pop("file", None)
        else:
            # we are changing some keys to make
            # them comapatible with the soundcloud api
            data = item.get("file", None)

        if (self.get_type(item) not in self.audio_types or
                       not data or
                       not "data" in data or
                       "_audio_url" in item):
            # if _audio_url is in the item, it was already uploaded
            # in a previous pipeline run
            raise NothingToDoHere
        file["asset_data"] = StringIO(data["data"])
        file["title"] = item.get("title", self.default_track_name)
        error = None
        self.logger.info("Uploading audio for item at %s" %
            item.get("_path", "<unknown>"))
        try:
            track = self.client.post("/tracks", data)
            status = track.status_code
        except HTTPError as error:
            status = 403
            # or some other, who knows?
        # 299 as in HTTP status - "200 Ok", > 300 some error
        if track.status_code > 399:
            logger.warn("Could not upload track for item %s :" % (
                      error if error else
                     "Soundcloud API returned HTTP status %d" % status))
            raise NothingToDoHere
        item["_audio_url"] = self.url_template.format(track_id=track.id)
        return item

@blueprint("sc.blueprints.soundcloud.register_id")
class Register(BluePrintBoiler):

    def set_options(self):
        self.record_file=self.options.get("record_file", "/tmp/sc.blueprints.soundcloud.uploaded.csv")

    def __iter__(self):
        already_recorded = self.storage.get("uploaded_audios", set())
        with open(self.record_file, "at") as records_:
            records = csv.writer(records_)
            for item in self.previous:
                try:
                    path = self.get_path(item)
                    if not "_audio_url" in item or path in already_recorded:
                        raise NothingToDoHere
                recorder.writerow((path, item["_audio_url"]))
                except NothingToDoHere:
                    pass
                yield item


