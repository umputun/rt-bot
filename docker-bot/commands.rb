class CommandHandler
  @@valid_commands = ['сколько можно про докер?',
                      'сколько можно про docker?',    
                      'сколько можно про эппл?',
                      'сколько можно про apple?',
                    ]

  def initialize(db, podcast)
    @db = db
    @podcast = podcast
  end

  def valid_commands
    return @@valid_commands
  end

  def exec(cmd)
    case cmd
    when 'сколько можно про докер?', 'сколько можно про docker?'
      count = @db.get_count(@podcast.get_current_podcast_number, 'docker')
      return "За текущий выпуск(№#{@podcast.get_current_podcast_number}) докер упоминали уже #{count} раз."
    when 'сколько можно про эппл?', 'сколько можно про apple?'
      count = @db.get_count(@podcast.get_current_podcast_number, 'apple')
      return "За текущий выпуск(№#{@podcast.get_current_podcast_number}) Apple упоминали уже #{count} раз."
    else
      return 'Так. Вы меня запутали.'
    end
  end
end