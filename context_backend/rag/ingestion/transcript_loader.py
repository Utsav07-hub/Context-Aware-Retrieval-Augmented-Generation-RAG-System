from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


class TranscriptLoader:

    def __init__(self, languages=None):
        self.languages = languages or ["en", "hi"]

    def extract_video_id(self, url: str) -> str:
        parsed_url = urlparse(url)

        # Normal YouTube URL
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
            if video_id:
                return video_id

        # youtu.be URL
        if parsed_url.hostname == "youtu.be":
            video_id = parsed_url.path.strip("/")
            if video_id:
                return video_id

        raise ValueError("Invalid YouTube URL")

    def load(self, video_url: str):
        video_id = self.extract_video_id(video_url)

        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=self.languages
        )

        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "snippets": transcript.to_raw_data(),
        }
