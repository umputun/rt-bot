require "sinatra"
require 'json'
require './db.rb'
require './podcast.rb'
require './commands.rb'

db = DatabaseHandler.new
podcast = PodcastHandler.new
cmd = CommandHandler.new(db, podcast)

words = [{:word => 'apple', :regex=> /apple|эппл/},
         {:word => 'docker', :regex=> /docker|докер/}
]

post '/event' do
  request.body.rewind
  @request_payload = JSON.parse request.body.read
  @podcast_number = podcast.get_current_podcast_number

  message = @request_payload['text']
  if cmd.valid_commands.include? message.downcase
    resp = {:text => cmd.exec(message.downcase), :bot => 'docker-bot'}
    content_type 'application/json'
    status 201
    body JSON.generate(resp)
  else
    words.each do |word|
      word_count = message.downcase.scan(word[:regex]).length
      db.add(@podcast_number,word[:word],word_count)
    end
    status 417
    body ''
  end
end

get '/info' do
  content_type 'application/json'
  info = {
    :author => 'https://github.com/naushniki',
    :info => 'Если в чате кто-то жалуется на то, что ведущие слишком долго обсуждают одну из своих излюбленных тем, этот бот сообщит, сколько раз та или иная тема была упомянута в чате в ходе текущего выпуска.',
    :commands => cmd.valid_commands
  }
  body JSON.generate(info)
end
