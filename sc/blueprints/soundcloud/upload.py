# coding: utf-8
# Author: João S. O. Bueno

import ast
import csv
from cStringIO import StringIO

import soundcloud
from requests.exceptions import HTTPError
#requests si not listed on the package requirements, but it is
# pre-requisite of the "soundcloud"

from DateTime import DateTime

from sc.transmogrifier.utils import blueprint
from sc.transmogrifier.utils import BluePrintBoiler
from sc.transmogrifier.utils import NothingToDoHere

from sc.blueprints.soundcloud import logger

# TODO: Audio url postponed to the blueprint
# responsible to actually making it a plone content
# attention to the "{track_id}" bit
SOUNDCLOUD_TEMPLATE_URL = ("http://w.soundcloud.com/player/?"
    "url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F"
    "{track_id}&amp;show_artwork=true")

@blueprint("sc.blueprints.soundcloud.upload")
class Upload(BluePrintBoiler):
    """Blueprint section for uploading audio files to
    soundcloud infrastructure.

    The "item" should have a "file" key, with a
    "data" section - withthe file data -
    optional sound file metada should be keys on item["file"]
    """
    def set_options(self):
        try:
            self.token = self.options["access_token"]
        except KeyError:
            # FIXME: allow other ways of fetching the access token.
            # TODO: create a Plone view to allow one to get a proper
            # token, to go with the product.
            logger.error("The sc.blueprints.soundcloud.upload blueprint"
                         " needs a valid soundcloud access token with"
                         " upload rights to be able to proceed. For now,"
                         " token should be passed as an \"acces_token\" "
                         "option on the cfg file. "
                         "This blueprint is **DISABLED** for this run")
            self.token = ""
        # Wether to remove the sound datafrom the item before dispacthing
        # it through the pipeline

        self.remove_data = ast.literal_eval(self.options.get(
            "remove_data", "True"))
        self.audio_types = ast.literal_eval(self.options.get(
            "audio_types", """("audio",)"""))
        self.url_template = self.options.get(
            "url_template", SOUNDCLOUD_TEMPLATE_URL)

        self.re_upload_existing = ast.literal_eval(self.options.get(
            "re_upload_existing", "False"))

        self.default_track_name = self.options.get(
                "default_track_name", "Plone audio file")
        # persitent text file to keep track of already uploaded
        # files
        self.record_file=self.options.get("record_file", "/tmp/sc.blueprints.soundcloud.uploaded.csv")

    def _log_uploaded_audio_iter(self):
        """
        Preserves the soundcloud ID of uploaded files
        so they an be retrieved from another pipeleine
        run building up plone objects - or even
        in case the creation of plone objects fail
        in the same pipeline
        """
        with open(self.record_file, "a+t") as records_:
            records = csv.writer(records_)
            while True:
                # Item is sent here at the end
                # of the main blueprint part
                # (transmogrify method)
                # which does not have to worry about
                # keeping track of the recorder file:
                item = yield None

                path = item.get("_path", "")
                if (not "_soundcloud_id" in item):
                    continue
                records.writerow((path, item["_soundcloud_id"]))
                self.already_recorded[path] = item["_soundcloud_id"]

    def pre_pipeline(self):

        try:
            self.client = soundcloud.Client(access_token = self.token)
        except HTTPError:
            logger.error("Could not retrieve a valid client to the"
                         " soundcloud API. Most likely the access_token"
                         " in the configuration is invalid or expired."
                         " Please check the docs on how to get a new token.\n"
                         "This blueprint is **DISABLED** for this run")
            self.client = None

        self.already_recorded = self.storage.get(
            "soundcloud_stored_ids", None)
        if not self.already_recorded:
            self.already_recorded = {}
            self.storage["soundcloud_stored_ids"] = self.already_recorded

        # make an in memor dict with the paths already recorded
        # and their soundcloud id's
        try:
            with open(self.record_file) as records_:
                records = csv.reader(records_)
                self.already_recorded = dict((row for row in records))
        except IOError: # likely teh file does not exist:
            self.already_recorded = dict()
        #starts the ID for the comming files
        self.log_uploaded_audio = self._log_uploaded_audio_iter()
        # and wind it to the point of getting the first item on
        # the pipeline:
        self.log_uploaded_audio.next()



    def post_pipeline(self):
        # ensure proper termination of the ID logger
        # so that the file is closed:
        del self.log_uploaded_audio

    def transmogrify(self, item):
        if self.remove_data:
            # NB.: the file is removed from item data
            # even if the soundcloud client is not up
            # and authorized:
            data = item.pop("file", None)
        else:
            # we are changing some keys to make
            # them comapatible with the soundcloud api
            data = item.get("file", None)

        if (self.get_type(item) not in self.audio_types or
                       not self.client or
                       not data or
                       not "data" in data or
                       "_audio_url" in item):
            # if _audio_url is in the item, it was already uploaded
            # in a previous pipeline run
            raise NothingToDoHere

        path = self.get_path(item)
        if path in self.already_recorded:
            if self.re_upload_existing:
                del self.already_recorded["path"]
            else:
                item["_soundcloud_id"] = self.already_recorded[path]
                return item
        file_ = {}
        file_["asset_data"] = StringIO(data["data"])
        file_["title"] = item.get("title", self.default_track_name)
        # SURPRISE! iT IS 2013, AND THEY GIVE YOU AN api THAT IS NOT
        # I18N AWARE!!!!!!!!!!!!
        if isinstance(file_["title"], unicode):
            file_["title"] = file_["title"].encode("utf-8")
        # Soundcloud fields: release_day, release_month, release_year
        
        # This is needed because in some pipelines
        # a non-existing date field may come up
        # as the string "None" (a 4 char str, not None,
        # the value)
        for date_field in ("effectiveDate",
                "modification_date", "creation_date"):
            date_str = item.get(date_field, None)
            if date_str and date_str.strip() != "None":
                break
        try:
            date = DateTime(date_str)
        except SyntaxError: # Yes, of all errors, the DateTime
                             # folk raise a "SyntaxError" :-/
            date = DateTime()
        if date == DateTime():
            logger.warn("Could not find date for object at %s, "
                    "setting as current timestamp" % path)
            date_str = str(date)
        file_["release_day"] = date.day()
        file_["release_month"] = date.month()
        file_["release_year"] = date.year()
        
        file_["created_at"] = date_str
        
        # TODO: add more metadata do the soundcloud track
        error = None
        logger.warn("Uploading audio for item at %s" %
            item.get("_path", "<unknown>"))
        try:
            track = self.client.post("/tracks", track=file_)
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
        item["_soundcloud_id"] = str(track.id)

        self.log_uploaded_audio.send(item)
        return item
