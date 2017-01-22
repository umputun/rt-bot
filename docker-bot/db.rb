require 'daybreak'

class DatabaseHandler
  @@flush_period = 30

  def initialize
      @db = Daybreak::DB.new "radio-t-docker-bot.db"
      @last_flush_performed = Time.now
  end

  def add(podcast_number, word, word_count)
    if @db[podcast_number] == nil
      @db[podcast_number] = {}
      @db[podcast_number][word]=word_count
    elsif @db[podcast_number][word] == nil
      @db[podcast_number][word]=word_count
    else
      @db[podcast_number][word]+=word_count
    end
    if Time.now - @last_flush_performed > @@flush_period
      self.flush
    end
  end

  def get_count(podcast_number, word)
    begin
      count = @db[podcast_number][word]
    rescue
      count = 0
    end
    return count
  end

  def flush
    @db.flush
  end

end