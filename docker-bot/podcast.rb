require 'rss'
require 'open-uri'

class PodcastHandler
  @@rss_feed_url = 'http://feeds.rucast.net/radio-t'
  def initialize
    @current_podcast_number = nil
    @last_time_podcast_number_was_successfully_detected = nil
    self.detect_current_podcast_number
  end

  def detect_current_podcast_number
    open(@@rss_feed_url) do |rss|
      feed = RSS::Parser.parse(rss, false)
      podcast_numbers = []
      feed.items.each do |item|
        number = item.title.scan(/\d\d\d/).last.to_i
        podcast_numbers.push(number)
      end
      @current_podcast_number = podcast_numbers.max+1
      @last_time_podcast_number_was_successfully_detected = Time.now
    end
  end

  def get_current_podcast_number
    begin
      if Time.now.saturday? and Time.now - @last_time_podcast_number_was_successfully_detected > 60*60*24
        self.detect_current_podcast_number
        return @current_podcast_number
      else
        return @current_podcast_number
      end
    rescue
      return @current_podcast_number
    end
  end

end